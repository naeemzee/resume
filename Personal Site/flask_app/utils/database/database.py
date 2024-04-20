import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users']
        
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
            
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id
    
    def getResumeData(self):
        resume_data = {}

        # Fetch institutions data
        institutions_query = "SELECT * FROM institutions"
        institutions_data = self.query(institutions_query)
        for institution in institutions_data:
            inst_id = institution['inst_id']
            resume_data[inst_id] = {
                'name': institution['name'],
                'type': institution['type'],
                'department': institution['department'],
                'address': institution['address'],
                'city': institution['city'],
                'state': institution['state'],
                'zip': institution['zip'],
                'positions': {}
            }

            # Fetch positions data for this institution
            positions_query = f"SELECT * FROM positions WHERE inst_id = {inst_id}"
            positions_data = self.query(positions_query)
            for position in positions_data:
                position_id = position['position_id']
                resume_data[inst_id]['positions'][position_id] = {
                    'title': position['title'],
                    'responsibilities': position['responsibilities'],
                    'start_date': position['start_date'],
                    'end_date': position['end_date'],
                    'experiences': {}
                }

                # Fetch experiences data for this position
                experiences_query = f"SELECT * FROM experiences WHERE position_id = {position_id}"
                experiences_data = self.query(experiences_query)
                for experience in experiences_data:
                    experience_id = experience['experience_id']
                    resume_data[inst_id]['positions'][position_id]['experiences'][experience_id] = {
                        'name': experience['name'],
                        'description': experience['description'],
                        'hyperlink': experience['hyperlink'],
                        'start_date': experience['start_date'],
                        'end_date': experience['end_date'],
                        'skills': {}
                    }

                    # Fetch skills data for this experience
                    skills_query = f"SELECT * FROM skills WHERE experience_id = {experience_id}"
                    skills_data = self.query(skills_query)
                    for skill in skills_data:
                        skill_id = skill['skill_id']
                        resume_data[inst_id]['positions'][position_id]['experiences'][experience_id]['skills'][skill_id] = {
                            'name': skill['name'],
                            'skill_level': skill['skill_level']
                        }

        return resume_data

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):
        # Check if the user already exists
        existing_user_query = "SELECT * FROM users WHERE email = %s"
        existing_user = self.query(existing_user_query, (email,))
        if existing_user:
            return {'success': 0, 'message': 'User already exists'}

        # Encrypt the password
        encrypted_password = self.onewayEncrypt(password)

        # Insert the user into the database
        insert_user_query = "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)"
        self.query(insert_user_query, (email, encrypted_password, role))

        return {'success': 1, 'message': 'User created successfully'}

    def authenticate(self, email='me@email.com', password='password'):
        # Hash the provided password using the same method as during user creation
        hashed_password = self.onewayEncrypt(password)

        # Query the database to check if the email and hashed password combination exist
        query = "SELECT * FROM users WHERE email = %s AND password = %s"
        parameters = (email, hashed_password)
        result = self.query(query, parameters)

        if result:
            # Authentication successful
            return {'success': 1}
        else:
            # Authentication failed
            return {'success': 0}

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message


