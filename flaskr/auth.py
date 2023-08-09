import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# associates the URL /register with the register view function, when Flask receives request to /auth/register, it will call the register view and use the return value as the response
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':          # if the user submitted the form, then this is 'POST'
        username = request.form['username']     # request.form = special type of dict mapping submitted form keys and values
        password = request.form['password']
        db = get_db()
        error = None
    
        # validate username and password are not empty
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:                       # if validate succeeds, insert the new user data into the database
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()      # generate_password_has modifies the data so this needs to be called afterward to save the changes
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()   # returns one row from the query

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # session is a dict that stores data across requests
        # when validation succeeds, the user's id is stored in a new session
        # data is stored in a cooke that is sent to the browser
        # the browser then sends it back with subsequent requests, Flask securely signs the data so that it can't be tampered with
        if error is None:
            session.clear()
            session['user_id'] = user['id']     # now the user's id is stored in the session and will be available on subsequent requests,  At the beginning of each request, if a user is logged in their information should be loaded and made available to other views
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# registers a function that runs before the view function, no matter what URL is requested
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')  # checks if user id is stored in the session

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(        # gets the user's data from the database storing it on g.user, which lasts for length of the request
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# now need to remove the user id from the session
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# creating, editing, and deleting blog posts requires the user to be logged in
# a decorator can be used to check this for each view it's applied to
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view

    # this decorator returns a new view function that wraps the original view it's applied to
    # The new function checks if a user is loaded and redirects to the login page otherwise. If a user is loaded the original view is called and continues normally
    # will use this decorator when writing the blog views
