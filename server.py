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
def movie_list():
    """Show list of users"""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/movies")
def user_list():
    """Show list of users"""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies = movies)

@app.route("/movies/<movie_id>")
def movie_details(movie_id):

    movie = Movie.query.get(movie_id)
    ratings = Rating.query.filter_by(movie_id= movie.movie_id).all()

    return render_template("movie_profile.html", ratings=ratings, movie=movie)


@app.route("/register", methods=["GET"])
def register_form():

    return render_template("register_form.html")



@app.route("/register", methods=["POST"])
def register_process():
    #code here

        #here is the info: turn args into variables
    email = request.form.get('email')
    password = request.form.get('password')

    user_email = User.query.filter_by(email = email)
    print type(user_email)

    if user_email.first():
        print 'already user'
        return redirect("/log_in")
    else:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        # session['user_id'] = User.query.get(user_id = new_user)
        db.session.commit()
        return redirect("/")


    # return redirect("/")

@app.route("/log_in", methods=["GET"])
def log_in_form():

    return render_template("log_in_form.html")



@app.route("/log_in", methods=["POST"])
def log_in_user():

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email = email, password = password)

        

        if user.first() is None:
            flash("Incorrect password")
            return redirect("/log_in")
        else:
            this_user = user.first()

            session['user_id'] = this_user.user_id

            #flash logged in
            flash("Logged In!")
            #add user id to session
            return redirect("/users/<user_id>")
        


@app.route("/log_out", methods=["GET"])
def log_out():
    
    session.clear()
    flash("Logged Out!")

    return redirect("/")



@app.route("/users/<user_id>", methods=["GET"])
def user_info(user_id): 

    user = User.query.get(user_id)

    ratings = Rating.query.filter_by(user_id = user.user_id).all()
    movies = []

    for r in ratings:
        movie = Movie.query.get(r.movie_id)
        movies.append(movie)

    combined = zip(ratings, movies)


    return render_template("user_profile.html", user =user, information = combined)



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
