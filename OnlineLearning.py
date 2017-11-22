from flask import Flask, render_template, redirect, request,url_for, session, g
import config
from models import User
from exts import db

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

@app.route('/')
def index():
    return 'This is index page!'

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter(User.email == email, User.password == password)
        if user:
            return redirect(url_for('index'))
        else:
            return u'Telephone or password is incorrect, please check your input and try again'


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        #email validation
        user = User.query.filter(User.email == email).first()
        if user:
            return u'This email address has already been registed, please change another E-mail address and try again!'
        else:
            # validate password and password2
            if password1 != password2:
                return u"The password is different from your first input, please check your input and try again! "
            else:
                user = User(email=email, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                # if user register successfully, redirect to log-in page.
                return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
