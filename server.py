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


@app.route("/movies")
def movie_list():
    """Show list of users"""

    #gets all movie objects
    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies = movies)

@app.route("/movies/<movie_id>")
def movie_details(movie_id):
    """Show all ratings for a particular movie"""

    #gets movie object from movie id
    movie = Movie.query.get(movie_id)

    #gets all ratings for that movie
    ratings = Rating.query.filter_by(movie_id= movie.movie_id).all()

    #adds movie id to current session
    session["current_movie_id"] = movie_id

    return render_template("movie_profile.html", ratings=ratings, movie=movie)


@app.route("/register", methods=["GET"])
def register_form():
    """Get for Register a New User."""

    return render_template("register_form.html")



@app.route("/register", methods=["POST"])
def register_process():
    """Checks if user email already exists in system.  If not, creates a new user."""

    #gets information from form
    email = request.form.get('email')
    password = request.form.get('password')

    #creates query for all users with entered email.
    user_email = User.query.filter_by(email = email)

    #checks if a user with that email exists, redirects to log in or creates user.
    if user_email.first():
        return redirect("/log_in")
    else:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        # session['user_id'] = User.query.get(user_id = new_user)
        db.session.commit()
        return redirect("/")




@app.route("/log_in", methods=["GET"])
def log_in_form():
    """Get for log in"""

    return render_template("log_in_form.html")



@app.route("/log_in", methods=["POST"])
def log_in_user():
    """Checks if user email and password match.  Logs user in if correct."""

    #gets variables from form
    email = request.form.get('email')
    password = request.form.get('password')


    #creates query for all users matching that email and password
    user = User.query.filter_by(email = email, password = password)

    
    #checks if password is correct, if not redirects back to log in page.
    if user.first() is None:
        flash("Incorrect password")
        return redirect("/log_in")
    else:
        this_user = user.first()

        session['user_id'] = this_user.user_id

        #flash logged in
        flash("Logged In!")
        #add user id to session

        redirect_string = "/users/" + str(this_user.user_id)
        # "/users" + "/<user_id>"


        return redirect(redirect_string)
        


@app.route("/log_out", methods=["GET"])
def log_out():
    """Clears session, logs user out"""
    
    session.clear()
    flash("Logged Out!")

    return redirect("/")



@app.route("/users/<user_id>", methods=["GET"])
def user_info(user_id): 
    """Shows all ratings for a particular user."""

    #gets user object from id
    user = User.query.get(user_id)

    #gets all ratings a particular user has done
    ratings = Rating.query.filter_by(user_id = user.user_id).all()
    movies = []

    #adds all movies that have a rating for that user to a movie list
    for r in ratings:
        movie = Movie.query.get(r.movie_id)
        movies.append(movie)

    #creates combined list of tuples of movies and their ratings
    combined = zip(ratings, movies)


    return render_template("user_profile.html", user =user, information = combined)



@app.route("/new_rating", methods=["GET"])
def add_new_rating_form():
    """Get for new rating."""

    return render_template("new_rating_form.html")



@app.route("/new_rating", methods=["POST"])
def add_new_rating():
    """Checks if user has rated movie before.  Updates rating if yes, adds a new rating if no."""

        #here is the info: turn args into variables

    #gets information from session
    movie_id = session["current_movie_id"]
    user_id = session['user_id']

    #gets new rating from form
    new_rating = request.form.get('rating')

    #creates query to get rating for that movie from that user
    current_rating_query = Rating.query.filter_by(movie_id=movie_id).filter_by(user_id=user_id)

    #gets rating object using query
    current_rating = current_rating_query.first()


    #checks if rating exists, if yes, update, if no, add
    if current_rating:
        flash('Rating Updated!')

        current_rating.score = new_rating
        #update rating here where to redirect?
        
    else:
        new_rating_complete = Rating(movie_id=movie_id, user_id= user_id, score = new_rating)

        db.session.add(new_rating_complete)
        # session['user_id'] = User.query.get(user_id = new_user)
        
    #commits to db 
    db.session.commit()

    #redirects to movie page
    redirect_string = "/movies/" + str(movie_id)
            # "/users" + "/<user_id>"


    return redirect(redirect_string)
        




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
