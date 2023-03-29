# app.py
from flask import get_flashed_messages, request, json, redirect, url_for, render_template, flash
from flask import Flask
from database import Database
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from utils import fetch_image, like_image, delete_image, upload_image
import datetime


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['JWT_SECRET_KEY'] = 'ece1779g4a3'  # Change this!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
db = Database()
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return render_template('signup.html', error_message='Passwords do not match')
        elif db.if_user_exist(username):
            return render_template('signup.html', error_message='Username already exists')
        else:
            # use bcrypt to hash the password
            password = bcrypt.generate_password_hash(password).decode('utf-8')
            db.put_user(username, password)
            return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('signup.html')


@app.route('/api/signin', methods=['POST'])
def sign_in():
    username = request.form['username']
    password = request.form['password']
    password_db = db.query_user(username, 'password')['password']
    
    if not password_db or not bcrypt.check_password_hash(password_db, password):
        return app.response_class(
            response = json.dumps({'success': 'false', 'error': 'Invalid username or password'}),
            status=401,
            mimetype='application/json'
        )

    else:
        access_token = create_access_token(identity=username)
        return app.response_class(
            response=json.dumps({'success':'true', 'access_token': access_token}),
            status=200,
            mimetype='application/json',
        )

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    username = get_jwt_identity()
    return app.response_class(
        response=json.dumps({'success':'true', 'username': username}),
        status=200,
        mimetype='application/json',
    )
    
@app.route('/api/images/<username>', methods=['GET'])
def get_images(username):
    images = fetch_image(db, username)
    print(images)
    return app.response_class(
        response=json.dumps({'success':'true', 'images': images}),
        status=200,
        mimetype='application/json',
    )
    
# like an picture
@app.route('/api/like', methods=['POST'])
def like():
    data = request.get_json()
    username = data.get('username')
    time = data.get('time')
    print(username)
    print(time)
    code = like_image(db, username, time)
    return app.response_class(
        response=json.dumps({'success':'true'}),
        status=code,
        mimetype='application/json',
    )

@app.route('/api/delete', methods=['POST'])
@jwt_required()
def del_image():
    data = request.get_json()
    username = get_jwt_identity()
    filename = data.get('filename')
    time = data.get('time')
    if username == data.get('username'):
        code = delete_image(db, username, time, filename)
        return app.response_class(
            response=json.dumps({'success':'true'}),
            status=code,
            mimetype='application/json',
        )
    else:
        return app.response_class(
            response=json.dumps({'success':'false', 'error': 'You are not allowed to delete this image'}),
            status=401,
            mimetype='application/json',
        )


@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload():
    username = get_jwt_identity()
    if db.if_user_exist(username): 
        image = request.files['image']
        description = request.form['description']
        filename = image.filename
        filetype = filename.split('.')[-1]
        
        code = upload_image(db, username, image, filetype, description)
        return app.response_class(
            response=json.dumps({'success':'true'}),
            status=code,
            mimetype='application/json',
        )
    return app.response_class(
        response=json.dumps({'success':'false', 'error': 'Invalid user'}),
        status=401,
        mimetype='application/json',
    )

# We only need this for local development.
if __name__ == '__main__':
    app.run()