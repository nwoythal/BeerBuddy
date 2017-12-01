"""Beer Database Backend."""
from flask import Flask, request, session, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./static/BeerSchema.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = None
db = SQLAlchemy(app)


class Beers(db.Model):
    """Object for the beers table."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    abv = db.Column(db.Float, nullable=False)
    # Break availibility into four seperate boolean fields.
    # 0 for all means that the beer has a limited run.
    # Determined in the beer view at render-time
    a_spr = db.Column(db.Integer, nullable=False)
    a_sum = db.Column(db.Integer, nullable=False)
    a_fal = db.Column(db.Integer, nullable=False)
    a_win = db.Column(db.Integer, nullable=False)
    brewery_id = db.Column(db.Integer, db.ForeignKey('breweries.id'),
                           nullable=False)


class Breweries(db.Model):
    """Object for the breweries table."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    zip_code = db.Column(db.Integer, db.ForeignKey('cities.zip_code'),
                         nullable=False)


class Cities(db.Model):
    """Object for the cities table."""

    zip_code = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Styles(db.Model):
    """Object for the styles table."""

    id = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.String(255), nullable=False)


class StylesIndex(db.Model):
    """Object for the styles_index table."""

    beer_id = db.Column(db.Integer, db.ForeignKey('beers.id'),
                        primary_key=True)
    style_id = db.Column(db.Integer, db.ForeignKey('styles.id'),
                         primary_key=True)


class Ratings(db.Model):
    """Object for the ratings table."""

    id = db.Column(db.Integer, primary_key=True)
    beer_id = db.Column(db.Integer, db.ForeignKey('beers.id'),
                        nullable=False)
    rating = db.Column(db.Float, nullable=False)


class RatingsBody(db.Model):
    """Object for the Ratings_Body table."""

    review_id = db.Column(db.Integer, db.ForeignKey('ratings.id'),
                          primary_key=True)
    review_body = db.Column(db.String(1024), nullable=False)


@app.route('/')
@app.route('/home')
@app.route('/home/')
def index():
    """Render the homepage."""
    return render_template('home.html')


# If we try to route to brewery without an ID, just give them the list.
@app.route('/beers')
@app.route('/beers/')
@app.route('/beer')
@app.route('/beer/')
def beers():
    """Render the list of beers. See beer() for individual beer page."""
    beer_list = Beers.query.join(Breweries, Beers.brewery_id ==
                                 Breweries.id).add_columns(Beers.name,
                                                           Beers.abv,
                                                           Beers.a_spr,
                                                           Beers.a_sum,
                                                           Beers.a_fal,
                                                           Beers.a_fal,
                                                           Breweries.name)
    return render_template('beers.html', beers=beer_list)


@app.route('/beer/<beer_id>', methods=['GET', 'POST'])
def beer(beer_id=None):
    """Render a unique beer. See beers() for the list."""
    # ID is unique, so just grab the first object
    if request.method == "POST":
        # Double check values, because I don't trust JavaScript
        try:
            rating_value = int(request.form.get('Beer_Rating'))
        except TypeError:
            rating_value = 999999  # Sentinel value to fail compare later
        rating_review = request.form.get('Beer_Review')
        # If the data is bad, someone is probably trying something malicious,
        # so throw the data out.
        if(rating_value > 10 or rating_value < 0 or len(rating_review) > 1024):
            rating_value = None
            rating_review = None
        else:
            new_rating = Ratings(beer_id=beer_id, rating=rating_value)
            db.session.add(new_rating)
            db.session.flush()
            if not new_rating.id:
                session.refresh(new_rating)  # Should give us an ID
            if len("Beer_Review"):
                new_rating_body = RatingsBody(review_id=new_rating.id,
                                              review_body=rating_review)
                db.session.add(new_rating_body)
                db.session.flush()
            db.session.commit()  # Commit changes to disk

    beer_result = Beers.query.filter(Beers.id == beer_id)[0]
    brewery_result = Breweries.query.filter(Breweries.id ==
                                            beer_result.brewery_id)[0]
    # Messy multi-assignment for 80-line limit
    styles_results = StylesIndex.query.join(Styles, StylesIndex.style_id ==
                                            Styles.id)
    styles_results = styles_results.filter(StylesIndex.beer_id == beer_id)
    styles_results = styles_results.add_columns(Styles.style)
    ratings_results = Ratings.query.join(Beers, Ratings.beer_id == Beers.id)
    ratings_results = ratings_results.outerjoin(RatingsBody, Ratings.id ==
                                                RatingsBody.review_id)
    ratings_results = ratings_results.filter(Ratings.beer_id == beer_id)
    ratings_results = ratings_results.add_columns(Ratings.rating,
                                                  RatingsBody.review_body)

    # Don't pass in empty query object.
    if not ratings_results.count():
        ratings_results = None

    # Lots of data passed in. We need the beer_id so we can properly POST,
    # and the rest is just query data so we can properly render everything.
    return render_template('beer.html', beer=beer_result,
                           brewery=brewery_result, styles=styles_results,
                           ratings=ratings_results, beer_id=beer_id)


# If we try to route to brewery without an ID, just give them the list.
@app.route('/breweries')
@app.route('/breweries/')
@app.route('/brewery')
@app.route('/brewery/')
def breweries():
    """Get the list of breweries. For individual breweries, see brewery()."""
    brewery_list = Breweries.query.join(Cities, Breweries.zip_code ==
                                        Cities.zip_code
                                        ).add_columns(Breweries.name,
                                                      Breweries.address,
                                                      Breweries.zip_code,
                                                      Cities.name)
    return render_template('breweries.html', breweries=brewery_list)


@app.route('/brewery/<brewery_id>')
def brewery(brewery_id=None):
    """Get an invidual brewery. For the list, see breweries()."""
    # ID is unique, so just grab the first object
    brewery_result = Breweries.query.filter(Breweries.id == brewery_id)[0]
    city_result = Cities.query.filter(Cities.zip_code ==
                                      brewery_result.zip_code)[0]
    beer_results = Beers.query.filter(Beers.brewery_id == brewery_id)
    return render_template('brewery.html', brewery=brewery_result,
                           city=city_result, beers=beer_results)


@app.errorhandler(404)
def page_not_found(error):
    """404 page not found."""
    return render_template('404.html'), 404
