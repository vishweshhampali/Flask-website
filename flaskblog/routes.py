import os
import secrets
from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, Fileupload
from flaskblog.models import User, File
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
def home():
	return render_template('index.html') 

@app.route("/about")
def about():
	return render_template('about.html') 

@app.route("/notes")
def notes():
	return render_template('notes.html') 

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/files",methods=['GET','POST'])
@login_required
def files():
    posts = File.query.all()
    return render_template('files.html',posts=posts)

def save_file(form_file):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_file.filename)
    file_fn = random_hex + f_ext
    file_path = os.path.join(app.root_path, 'static/files', file_fn)
    form_file.save(file_path)
    return file_fn

@app.route("/upload",methods=['GET','POST'])
@login_required
def uploadfile():
    upload=Fileupload()
    if upload.validate_on_submit():
        print('hello')
        if upload.uploadfile.data:
            file_name = save_file(upload.uploadfile.data)
            file = File(writername=upload.writername.data, subjectname=upload.subjectname.data, filename=file_name)
            db.session.add(file)
            db.session.commit()
            flash('Your notes have been uploaded!', 'success')
            return redirect(url_for('home'))
    return render_template('upload.html',upload=upload)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))



app.run(debug=True)