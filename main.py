from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests
from pprint import pprint

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI']= "sqlite:/// movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Movie(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(300), nullable=True)
    img_url = db.Column(db.String(300), nullable=False)


class RatingMovieForm(FlaskForm):
    ratings = FloatField(label='Your rating', validators=[DataRequired()])
    reviews = StringField(label='Your review', validators=[DataRequired()])
    submit = SubmitField(label='done')

class AddMovie(FlaskForm):
    movie_title = StringField(label='Movie Title', validators=[DataRequired()])
    submit= SubmitField(label='enter')


API_KEY ='f84e9449c92b6dbd907b7ea9b0daedbb'
API_ACCESS_TOKEN= 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmODRlOTQ0OWM5MmI2ZGJkOTA3YjdlYTliMGRhZWRiYiIsInN1YiI6IjYxZTI4N2I2Y2IzMDg0MDA2OGViOWEzMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.rB1Cv6eecBR-86OzZxIo4_aTxquaxJQtq7fDBn42-Yw'
API_URL ='https://api.themoviedb.org/3/movie/550'


db.session.commit()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies)-i
    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route("/edit", methods= ["GET", "POST"])
def rate_movie():
    form = RatingMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.ratings.data)
        movie.review = form.reviews.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, form=form)




@app.route('/delete')
def delete_movie():
    movie_id=request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))




@app.route('/add', methods=['GET', 'POST'])
def add_movie():
    form = AddMovie()
    if form.validate_on_submit():
        title = form.movie_title.data
        parameters = {
            'api_key': API_KEY,
            'query': title,
            'id':597
        }
        response = requests.get(url='https://api.themoviedb.org/3/search/movie', params=parameters)
        movie_data = response.json()['results']
        #print(movie_data)
        #for movie_search in movie_data:
           # print(f"{movie_search['title']} - {movie_search['release_date']}-{movie_search['id']}")

        return render_template('select.html', movie_results=movie_data)

    return render_template('add.html', form=form)




@app.route('/display', methods=["GET", "POST"])
def display_movie():
    movie_api_id = request.args.get('the_id')
    parameters_2 = {
        "api_key": API_KEY,
    }
    header ={
        "Authorization": f'Bearer{API_ACCESS_TOKEN}',
        'Content-type': 'application/json;charset=utf-8'
    }
    response = requests.get( url=f"https://api.themoviedb.org/3/movie/{movie_api_id}", params=parameters_2, headers=header)
    the_data = response.json()
    new_movie = Movie(
        title = the_data['title'],
        year= the_data['release_date'].split("-")[0],
        description = the_data['overview'],
        img_url=f'{"https://image.tmdb.org/t/p/w500/"}{the_data["poster_path"]}'
    )
    db.session.add(new_movie)
    db.session.commit()
    #print(the_data)
    #print(movie_api_id)
    return redirect(url_for('rate_movie', id=new_movie.id))





if __name__ == '__main__':
    app.run(debug=True)






