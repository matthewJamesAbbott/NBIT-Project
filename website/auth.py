import random
import string
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   # means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import re
from redmail import gmail

auth = Blueprint('auth', __name__)

# endpoint for login information to be sent and access recieved or denied.
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        # Remove any HTML tags using regex
        email = re.sub(r'<[^>]*>', '', email)
        # Escape special characters to prevent SQL injection
        email = email.replace("'", "''")
        email = email.replace('"', '""')


        password = request.form.get('password')

        # test users login data and either login user or deny access
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password): # hash given password then test against encryprted hash in database
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


# endpoint for loging user out of application
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# endpoint for sending sign up details and receive comformation or rejection
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        # Remove any HTML tags using regex
        email = re.sub(r'<[^>]*>', '', email)
        # Escape special characters to prevent SQL injection
        email = email.replace("'", "''")
        email = email.replace('"', '""')

        first_name = request.form.get('firstName')
        # Remove any HTML tags using regex
        first_name = re.sub(r'<[^>]*>', '', first_name)
        # Escape special characters to prevent SQL injection
        first_name = first_name.replace("'", "''")
        first_name = first_name.replace('"', '""')

        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        # catch errors for existing accounts and password errors
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')

        # details are correct process details
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256')) # encrypt password into hash with sha256 algorithm
            db.session.add(new_user) # add new user to user database
            db.session.commit() # commit changes to database
            login_user(new_user, remember=True) # log user into account that was created
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

# endpoint for user to change password
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('oldPassword')
        new_password1 = request.form.get('newPassword1')
        new_password2 = request.form.get('newPassword2')

        # test old password to see if it is correct
        if not check_password_hash(current_user.password, old_password):
            flash('Old password is incorrect.', category='error')
        elif new_password1 != new_password2:
            flash('New passwords don\'t match.', category='error')
        elif len(new_password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            current_user.password = generate_password_hash(new_password1, method='pbkdf2:sha256')
            db.session.commit()
            flash('Password changed!', category='success')
            return redirect(url_for('views.home'))

    return render_template("change_password.html", user=current_user)

# endpoint for user to delete account
@auth.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        password = request.form.get('password')

        # test password to see if it is correct
        if not check_password_hash(current_user.password, password):
            flash('Password is incorrect.', category='error')
        else:
            db.session.delete(current_user)
            db.session.commit()
            logout_user()
            flash('Account deleted.', category='success')
            return redirect(url_for('auth.login'))

    return render_template("delete_account.html", user=current_user)

# endpoint for email of temporary password
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Remove any HTML tags using regex
        email = re.sub(r'<[^>]*>', '', email)
        # Escape special characters to prevent SQL injection
        email = email.replace("'", "''")
        email = email.replace('"', '""')

        user = User.query.filter_by(email=email).first()

        # test email to see if it exists
        if user:
            # generate random temporary password
            temp = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            # create temporary password
            user.password = generate_password_hash(temp, method='pbkdf2:sha256')
            db.session.commit()
            # send email with temporary password
            gmail.username = 'your_address@gmail.com' # Your Gmail address
            gmail.password = 'your_app_key' # Your App Passkey

            # And then you can send emails
            gmail.send(
                subject="Temporary Password",
                receivers=[email],
                text=temp
            )
            flash('An email has been sent with a temporary password', category='success')
        else:
            flash('Email does not exist.', category='error')


    return render_template("forgot_password.html", user=current_user)
