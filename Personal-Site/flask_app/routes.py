from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from .utils.database.database import database
from pprint import pprint
import json
import random
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
    return session['email'] if 'email' in session else 'Unknown'

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
                session['email'] = email
                # Return success status as a JSON response
                return json.dumps({'success': 1})
        
        # Authentication failed, return failure status with a message
        return json.dumps({'success': 0, 'message': 'Invalid email or password'})

    # Redirect to the login page for GET requests
    elif request.method == 'GET':
        return redirect(url_for('login'))

#######################################################################################
# CHATROOM RELATED
#######################################################################################

# Route for the chat page (requires login)
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser())

# SocketIO event handler for user joining the chat
@socketio.on('joined', namespace='/chat')
def joined(message):
    join_room('main')
    # Check if the user joining is the owner and emit appropriate status message
    if getUser() == "owner@email.com":
        emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
    else:
        emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:grey;text-align: left'}, room='main')

# SocketIO event handler for handling user messages
@socketio.on('message', namespace='/chat')
def handle_message(message):
    sender = getUser()
    # Check if the message sender is the owner and emit appropriate status message
    if getUser() == "owner@email.com":
        emit('status', {'msg': message, 'sender': sender, 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
    else:
         emit('status', {'msg': message, 'sender': sender, 'style': 'width: 100%;color:grey;text-align: left'}, room='main')

# SocketIO event handler for user disconnecting from the chat
@socketio.on('handle_disconnect', namespace='/chat')
def handle_disconnect(message):
    # Check if the user disconnecting is the owner and emit appropriate status message
    if getUser() == "owner@email.com":
        emit('status', {'msg': getUser() + ' has left the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
    else:
        emit('status', {'msg': getUser() + ' has left the room.', 'style': 'width: 100%;color:grey;text-align: left'}, room='main')

#######################################################################################
# OTHER
#######################################################################################

# Route for the root URL, redirects to home
@app.route('/')
def root():
    return redirect('/home')

# Route for the home page
@app.route('/home')
def home():
    # Dummy data retrieval
    print(db.query('SELECT * FROM users'))
    x = random.choice(['I played on the tennis team in high school.','I watch sports like the NFL, NBA, and NHL.','I like to play video games like Elden Ring.'])
    return render_template('home.html', user=getUser(), fun_fact=x)

# Route to process feedback form submission
@app.route('/processfeedback', methods=['POST'])
def processfeedback():
    feedback = request.form
    name = feedback['name']
    email = feedback['email']
    comment = feedback['comment']
    if name != '' and comment != '':
        db.insertRows('feedback', ['name', 'email', 'comment'], [[name, email, comment]])
    stored_feed = db.query('SELECT * FROM feedback')
    return render_template('processfeedback.html', stored_feed=stored_feed)

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
