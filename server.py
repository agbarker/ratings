"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users"""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/register", methods=["GET"])
def register_form():

    return render_template("register_form.html")



@app.route("/register", methods=["POST"])
def register_process():
    #code here

        #here is the info: turn args into variables
    email = request.form.get('email')
    password = request.form.get('password')

    users = User.query.all()

    existing_user = False


    for user in users:
        if user.email == email and user.password == password:
            existing_user = True
            log_user_id = user.user_id

            break

    if existing_user == True:
        #flash logged in
        flash("Logged In!")
        #add user id to session
        session['user_id'] = log_user_id


    if existing_user == False:
        new_user = User(email=email, password=password)
        db.session.add(new_user)

    db.session.commit()


    return redirect("/")


@app.route("/log_out", methods=["GET"])
def log_out():
    session["user_id"] = None
    flash("Logged Out!")

    return redirect("/")




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
