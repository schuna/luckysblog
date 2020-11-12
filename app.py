import os

from flask import Flask, request, jsonify, render_template, request, session, redirect, flash, url_for
from flask_jwt import JWT
from security import authenticate, identity as identity_function

from datetime import timedelta
from models.user import UserModel

app = Flask(__name__)

app.config['DEBUG'] = True
app.secret_key = 'jiyong'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


jwt = JWT(app, authenticate, identity_function)

@jwt.auth_response_handler
def customized_response_handler(access_token, identity):
    return jsonify({
                'access_token': access_token.decode('utf-8'),
                'user_id': identity.id
            })


@jwt.jwt_error_handler
def customized_error_handler(error):
    return jsonify({
                'message': error.description,
                'code': error.status_code
                }), error.status_code


@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)

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
    if session.get('username'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        user_id = UserModel.count()
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



if __name__ == '__main__':
    from db import db
    db.init_app(app)
    if app.config['DEBUG']:
        @app.before_first_request
        def create_tables():
            db.create_all()

    app.run(port=5000)
