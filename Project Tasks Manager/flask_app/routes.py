from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from .utils.database.database import database
from pprint import pprint
import json
import functools
from . import socketio

# Initialize database
db = database()

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################

# Decorator to ensure login requirement for certain routes
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

# Function to get user's email from session
def getUser():
    if 'email' in session:
        user_email = db.reversibleEncrypt('decrypt', session['email']) 
        return user_email

    return 'Unknown'

# Route for login page
@app.route('/login')
def login():
    return render_template('login.html')

# Route for logout
@app.route('/logout')
def logout():
    session.pop('email', default=None)
    return redirect('/')

# Route to process login form submission
@app.route('/processlogin', methods=["POST", "GET"])
def processlogin():
    if request.method == 'POST':
        # Extract email and password from the form data
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email and password are not None or empty strings
        if email and password:
            # Call the authenticate method with the provided email and password
            authentication_result = db.authenticate(email, password)

            # Check if authentication is successful
            if authentication_result['success'] == 1:
                # Update the session with the email
                session['email'] = db.reversibleEncrypt('encrypt', email)
                # Return success status as a JSON response
                return json.dumps({'success': 1})
        
        # Authentication failed, return failure status with a message
        return json.dumps({'success': 0, 'message': 'Invalid email or password'})

    # Redirect to the login page for GET requests
    elif request.method == 'GET':
        return redirect(url_for('login'))
    
# Route to process sign up form submission
@app.route('/processsignup', methods=["POST", "GET"])
def processsignup():
    if request.method == 'POST':
        # Extract email and password from the form data
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email and password are not None or empty strings
        if email and password:
            # Call the authenticate method with the provided email and password
            create_user_result = db.createUser(email, password)

            # Check if authentication is successful
            if create_user_result['success'] == 1:
                # Update the session with the email
                session['email'] = db.reversibleEncrypt('encrypt', email)
                # Return success status as a JSON response
                return json.dumps({'success': 1})
        
        # Sign up failed, return failure status with a message
        return json.dumps({'success': 0, 'message': 'Invalid email'})

    # Redirect to the login/signup page for GET requests
    elif request.method == 'GET':
        return redirect(url_for('login'))

#######################################################################################
# CHATROOM RELATED
#######################################################################################

# SocketIO event handler for user joining the chat
@socketio.on('joined', namespace='/board')
def joined(data):
    join_room(data['boardId'])
    # Emit appropriate status message
    emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:grey;text-align: left'}, room=data['boardId'])

# SocketIO event handler for handling user messages
@socketio.on('message', namespace='/board')
def handle_message(data):
    sender = getUser()
    emit('status', {'msg': getUser() + ': ' + data['message'], 'sender': sender, 'style': 'width: 100%;color:grey;text-align: left'}, room=data['boardId'])

# SocketIO event handler for user disconnecting from the chat
@socketio.on('handle_disconnect', namespace='/board')
def handle_disconnect(data):
    # Emit appropriate status message
    emit('status', {'msg': getUser() + ' has left the room.', 'style': 'width: 100%;color:grey;text-align: left'}, room=data['boardId'])
    leave_room(data['boardId'])

#######################################################################################
# OTHER
#######################################################################################

# Route for the root URL, redirects to home
@app.route('/')
@login_required
def root():
    return redirect('/home')

# Route for the home page
@app.route('/home')
@login_required
def home():
    # SQL query to retrieve user_id based on email
    query = "SELECT user_id FROM users WHERE email = %s"
    user_id = db.query(query, (getUser(),))

    # Query the database to get the boards associated with the user
    query = "SELECT * FROM boards WHERE user_id = %s"
    user_boards = db.query(query, (user_id[0]['user_id'],))

    # Query the database to get the boards
    query = "SELECT * FROM boards"
    all_boards = db.query(query)

    return render_template('home.html', user_boards=user_boards, all_boards=all_boards, user=getUser())

# Route to serve static files
@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

# Function to add headers to response to prevent caching
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

# Route to process new board form submission
@app.route('/processnewboard', methods=["POST"])
def processnewboard():
    if request.method == 'POST':
        # Extract name and emails from the form data
        name = request.form.get('name')
        emails = request.form.get('emails')

        # SQL query to retrieve all users
        query = "SELECT * FROM users"
        users = db.query(query)

        # Split emails by commas and remove leading/trailing spaces from each
        emails_list = [email.strip() for email in emails.split(',')]

         # Get a list of registered emails
        registered_emails = [user['email'] for user in users]

        # Check if all emails are registered
        all_registered = all(email in registered_emails for email in emails_list)

        if name and emails_list == [''] or name and all_registered:
            # SQL query to retrieve user_id based on email
            query = "SELECT user_id FROM users WHERE email = %s"
            user_id = db.query(query, (getUser(),))

            # Call the create board method with the provided name, emails, and user id
            create_board_result = db.createBoard(name, emails, user_id[0]['user_id'])

            # Check if board creation is successful
            if create_board_result['success'] == 1:
                # Return success status as a JSON response
                return json.dumps({'success': 1, 'board_id': create_board_result['board_id']})
        
        # Sign up failed, return failure
        return json.dumps({'success': 0})
    
# SocketIO event handler for user joining the baord
@socketio.on('live', namespace='/board')
def live(data):
    join_room(data['boardId'])
    
@socketio.on('new_card_created', namespace='/board')
def new_card_created(data):
    # Process the new card creation
    # Emit a message to notify other users
    emit('card_created', data, room=data['boardId'])

@socketio.on('handle_text', namespace='/board')
def handle_text(data):
    # Process the new card creation
    # Emit a message to notify other users
    emit('card_text', data, room=data['boardId'])

@socketio.on('handle_drop', namespace='/board')
def handle_drop(data):
    # Process the new card creation
    # Emit a message to notify other users
    emit('card_drop', data, room=data['boardId'])

@socketio.on('handle_delete', namespace='/board')
def handle_delete(data):
    # Process the new card creation
    # Emit a message to notify other users
    emit('card_delete', data, room=data['boardId'])
    
@app.route('/board')
def board():
    board_id = request.args.get('board_id')

    # SQL query to retrieve board name based on board id
    query = "SELECT board_name FROM boards WHERE board_id = %s"
    board_name = db.query(query, (board_id,))

    # SQL query to retrieve cards based on board id
    query = "SELECT * FROM cards WHERE board_id = %s"
    board_cards = db.query(query, (board_id,))

    # SQL query to retrieve all cards
    query = "SELECT * FROM cards"
    all_cards = db.query(query)

    return render_template('board.html', board_name=board_name[0]['board_name'], all_cards=all_cards, board_id=board_id, board_cards=board_cards, user=getUser())

# Route to process card info
@app.route('/processcardinfo', methods=["POST"])
def processcardinfo():
    if request.method == 'POST':
        # Extract text, card id, board id, and list id from the form data
        card_text = request.form.get('cardText')
        list_id = request.form.get('listId')
        card_id = request.form.get('cardId')
        board_id = request.form.get('boardId')

        db.cardInfo(board_id, card_text, card_id, list_id)

        return json.dumps({'success': 1})


# Route to process new board form submission
@app.route('/processdeletecard', methods=["POST"])
def processdeletecard():
    if request.method == 'POST':
        # Extract card id and board id from the form data
        card_id = request.form.get('cardId')
        board_id = request.form.get('boardId')

        db.cardDelete(board_id, card_id)
