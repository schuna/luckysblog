import os
import logging

from flask import Flask, request, jsonify, render_template, request, session, redirect, flash, url_for
from security import authenticate, identity as identity_function
from werkzeug.utils import secure_filename

from models.user import UserModel
from models.post import Posts

app = Flask(__name__)

app.config['DEBUG'] = True
app.secret_key = 'jiyong'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ALLOWED_EXTENTIONS = set(['png', 'jpg', 'jpeg', 'gif'])


@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", Posts = Posts.get_list_of_dict(), index=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = UserModel.find_by_email(email=email)
        if user and user.get_password(password):
            session['user_id'] = user.user_id
            session['username'] = user.first_name
            return redirect("/index")
        else:
            flash("Sorry, email or passwrd is wrong!", "danger")
    return render_template("login.html", signin=True)


@app.route("/logout")
def logout():
    session['user_id'] = False
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if not session.get('username'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        user_id = UserModel.count()
        app.logger.info(user_id)
        user_id += 1
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        user = UserModel(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        flash("You are successfully registered!", "success")
        return redirect(url_for('index'))

    return render_template('register.html', register=True)


@app.route("/dbview")
def dbview():
    data = []
    if not session.get('username'):
        return redirect(url_for('index'))
    return render_template("dbview.html", Users = UserModel.get_list_of_dict(), Posts = Posts.get_list_of_dict(), dbview=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENTIONS

@app.route("/uploadimg", methods=["GET", "POST"])
def uploadimg():
    user = UserModel.find_by_id(user_id=session['user_id'])

    if request.method == "POST":
        description = request.form.get('description')
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            static_path = os.path.join('static', 'images')
            # file save
            abs_path = os.path.join(os.getcwd(), static_path)
            local_path = os.path.join(abs_path, filename)
            file.save(local_path)
            # db update
            relative_path = os.path.join('.', static_path)
            url_path = os.path.join(relative_path, filename)
            post = Posts(description=description, image_path=url_path, user_id=user.user_id)
            post.save()
            flash("Successfully uploaded!", "success")
            return render_template("dbview.html", Users = UserModel.get_list_of_dict(), Posts = Posts.get_list_of_dict(), dbview=True)
        else:
            flash("Somethings went wrong!", "danger")

    return render_template("uploadimg.html", uploadimg=True)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not session.get('username'):
        return redirect(url_for('index'))
    user = UserModel.find_by_id(user_id=session['user_id'])
    if request.method == "POST":
        description = request.form.get('description')
        image_path = request.form.get('image_path').split('?')[0].replace("view", "preview")
        try:
            post = Posts(description=description, image_path=image_path, user_id=user.user_id)
            post.save()
            flash("Successfully uploaded!", "success")
            return render_template("dbview.html", Users = UserModel.get_list_of_dict(), Posts = Posts.get_list_of_dict(), dbview=True)
        except:
            flash("Somethings went wrong!", "danger")
            return redirect(url_for('index'))
    return render_template("upload.html", upload=True)


@app.route('/delete/<post_id>', methods=['GET', 'POST'])
def delete(post_id):
    if not session.get('username'):
        return redirect(url_for('index'))
    try:
        post = Posts.find_by_id(post_id)
        post.delete()
        flash("Successfully deleted!", "success")
    except:
        flash("Somethings went wrong!", "danger")
    return redirect(url_for('index'))


if __name__ == '__main__':
    from db import db
    db.init_app(app)
    if app.config['DEBUG']:
        @app.before_first_request
        def create_tables():
            db.create_all()

    app.run(host='0.0.0.0', port=5000)
