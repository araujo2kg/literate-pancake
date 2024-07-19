import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db


# url_prefix will be present before every route set in this bp, so if we have an /register route, the url would be /auth/register
bp = Blueprint('auth', __name__, url_prefix='/auth')

# we use the bp instance the same way as we would be using the application instance
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username'] # request.form.get('username', default), safer
        password = request.form['password']

        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                    error = f"User {username} is already registered."
            # This conditional is part of the try block, it runs if no exception is raised in the try block (not just IntegrityError) 
            else:
                # When using redirect, use the url_for, not the hardcoded path, url_for receives the view function and return the path
                return redirect(url_for("auth.login"))
        flash(error)
    return render_template('auth/register.html')

    
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username'] # request.form.get('username', default), safer
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username)
        ).fetchone()
        # fetchone returns one row from the query, if query gives no results, it returns None

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
    return render_template('auth/login.html')

        