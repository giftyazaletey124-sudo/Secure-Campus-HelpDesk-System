
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if 'user_id' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('main.login'))

        return function(*args, **kwargs)

    return wrapper

def role_required(*allowed_roles):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if 'user_id' not in session:
                flash('Please log in first.')
                return redirect(url_for('main.login'))

            if session.get('user_role') not in allowed_roles:
                flash('You are not authorized to access this page.')
                return redirect(url_for('main.home'))

            return function(*args, **kwargs)

        return wrapper

    return decorator