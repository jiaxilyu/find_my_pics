# app.py
from flask import request, json, redirect, url_for, render_template
from flask import Flask
from database import Post, User
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from utils import fetch_image, like_image, delete_image, upload_image, explore_image, search as utils_search
# from post import Post

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['JWT_SECRET_KEY'] = 'ece1779g4a3'  # Change this!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
db_post = Post()
db_user = User()
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route('/profile')
def profile_page():
    get_post_view_endpoint = 'https://p0kon76pkg.execute-api.us-east-1.amazonaws.com/default/get-post-views'
    return render_template('profile.html', get_post_view_endpoint=get_post_view_endpoint)

@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    if request.args.get("content"):
        content = request.args.get("content")
        posts = utils_search(db_post, content, 20)
        return render_template('search.html', posts=posts, num_posts=(len(posts) if len(posts) > 0 else -1))
    else:
        return render_template('search.html')

@app.route('/explore')
def explore():
    report_post_view_endpoint = 'https://qp0jvpfqhb.execute-api.us-east-1.amazonaws.com/default/report-post-view-event'
    posts = explore_image(db_post, 20)
    return render_template('explore.html', posts=posts, report_post_view_endpoint=report_post_view_endpoint)

@app.route('/explore/user/<username>')
def explore_user(username):
    report_post_view_endpoint = 'https://qp0jvpfqhb.execute-api.us-east-1.amazonaws.com/default/report-post-view-event'
    posts = fetch_image(db_post, username)
    return render_template('explore.html', username=username, posts=posts, report_post_view_endpoint=report_post_view_endpoint)

@app.route('/explore/label/<label>')
def explore_label(label):
    report_post_view_endpoint = 'https://qp0jvpfqhb.execute-api.us-east-1.amazonaws.com/default/report-post-view-event'
    posts = utils_search(db_post, label, 20)
    return render_template('explore.html', label=label, posts=posts, report_post_view_endpoint=report_post_view_endpoint)


@app.route('/signup', methods=['GET'])
def sign_up():
    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def sign_up_user():
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        return app.response_class(
            response = json.dumps({'success': 'false', 'error': 'Passwords do not match'}),
            status=401,
            mimetype='application/json'
        )
    elif db_user.if_user_exist(username):
        return app.response_class(
            response = json.dumps({'success': 'false', 'error': 'Username already exists'}),
            status=401,
            mimetype='application/json'
        )
    else:
        # use bcrypt to hash the password
        password = bcrypt.generate_password_hash(password).decode('utf-8')
        db_user.put_user(username, password)
        return app.response_class(
            response = json.dumps({'success': 'true'}),
            status=200,
            mimetype='application/json'
        )


@app.route('/api/signin', methods=['POST'])
def sign_in():
    username = request.form['username']
    password = request.form['password']
    if username == '' or password == '':
        return app.response_class(
            response = json.dumps({'success': 'false', 'error': 'Please enter username and password'}),
            status=401,
            mimetype='application/json'
        )
    
    password_db = db_user.query_user(username, 'password')['password']
    
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
    images = fetch_image(db_post, username)
    return app.response_class(
        response=json.dumps({'success':'true', 'images': images}),
        status=200,
        mimetype='application/json',
    )
    
# like an picture
@app.route('/api/like', methods=['POST'])
@jwt_required()
def like():
    username = get_jwt_identity()
    data = request.get_json()
    post_id = data.get('post_id')
    code = like_image(db_post, username, post_id)
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
    post_id = data.get('post_id')
    filename = data.get('filename')
    if username == db_post.get_post(post_id)['user_name']:
        code = delete_image(db_post, post_id, filename)
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
    if db_user.if_user_exist(username):
        image = request.files['image']
        description = request.form['description']
        filename = image.filename
        filetype = filename.split('.')[-1]
        
        code = upload_image(db_post, username, image, filetype, description)
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
    pass