#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import sys
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:admin@127.0.0.1:5432/fyyur'

# the migration proccess

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand);

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#



class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String())
    is_seeking = db.Column(db.Boolean(), default=False)
    seeking_desc = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)

    def __repr__(self):
      return f'<name: {self.name}, city: {self.city}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    is_seeking = db.Column(db.Boolean, default=False)
    seeking_desc = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)

    def __repr__(self):
      return f'<name: {self.name}, city: {self.city}>'
# adding the show model ( Child )
class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  date_time = db.Column(db.DateTime, nullable=False)
  
  def __repr__(self):
    return f'<Id: {self.id}, Artist: {self.artist_id}, Venue: {self.venue_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venue = Venue.query.all()
  data = []
  check = []
  for i in venue:
    venues = []
    dictionary = {
      "city": i.city,
      "state": i.state,
    }
    if not i.city in check:
      check.append(i.city)
      venues.append({
        "id": i.id,
        "name": i.name
      })
    dictionary["venues"] = venues
    data.append(dictionary)
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form['search_term']
  venues = Venue.query.all()
  data = []
  response = {
    "count": 0
  }
  for i in venues:
    if search_term in i.name:
      response["count"] += 1
      data.append({
        "id": i.id,
        "name": i.name
      })
      response["data"] = data
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.get(venue_id)
  print(data.shows)
  their_shows = []
  for show in data.shows:
    their_shows.append({
      "id": show.artist.id,
      "image": show.artist.image_link,
      "name": show.artist.name,
      "datetime": str(show.date_time)
    })
  return render_template('pages/show_venue.html', venue=data, shows=their_shows)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    is_seeking = True if 'is_seeking' in request.form else False
    seeking_desc = request.form['seeking_desc']
    genres = request.form['genres']
    website = request.form['website']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, is_seeking=is_seeking, seeking_desc=seeking_desc, genres=genres, website=website, image_link=image_link, facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()
  
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('Something went wrong while creating ' + data.name)
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  print(data)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_value = request.form['search_term']
  response = {
    "data":[],
    "count": 0
  }
  for i in Artist.query.all():
    if search_value in i.name or search_value == i.state or search_value in i.city:
      response["data"].append(i)
      response["count"] += 1
  
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.get(artist_id)
  his_shows=[]
  for show in data.shows:
    print(show.id)
    his_shows.append({
      "id": show.venue.id,
      "image": show.venue.image_link,
      "name": show.venue.name,
      "datetime": str(show.date_time)
    })
  return render_template('pages/show_artist.html', artist=data, shows=his_shows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form['genres']
    is_seeking = True if 'is_seeking' in request.form else False
    seeking_desc =  request.form['seeking_desc']
    website = request.form['website']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    artist = Artist.query.get(artist_id) # Getting the artist using artist_id.
    # Changing the actual value with the data from the edit form.
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.genres = genres
    artist.is_seeking = is_seeking
    artist.seeking_desc = seeking_desc
    artist.website = website
    artist.image_link = image_link
    artist.facebook_link = facebook_link
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form['genres']
  website = request.form['website']
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  venue = Venue.query.get(venue_id)
  venue.name = name
  venue.city = city
  venue.state = state
  venue.address = address
  venue.phone = phone
  venue.genres = genres
  venue.website = website
  venue.image_link = image_link
  venue.facebook_link = facebook_link
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form['genres']
    is_seeking = True if 'is_seeking' in request.form else False
    seeking_desc = request.form['seeking_desc']
    website = request.form['website']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, is_seeking=is_seeking, seeking_desc=seeking_desc, website=website, image_link=image_link, facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(str(sys.exc_info()))
    flash('Something went wrong while creating ' + request.form['name'])
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.join(Artist).join(Venue).all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.date_time.strftime("%Y-%m-%d %H:%M:%S")
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    artist_id = request.form["artist_id"]
    venue_id = request.form["venue_id"]
    start_date = request.form["start_time"]
    show = Show(artist_id=artist_id, venue_id=venue_id, date_time=start_date)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    print(current_time)
    print(start_date)
    print(Artist.query.get(artist_id).upcoming_shows_count)
    if start_date > current_time:
      Artist.query.get(artist_id).upcoming_shows_count += 1
      Venue.query.get(venue_id).upcoming_shows_count += 1
    elif start_date < current_time:
      Artist.query.get(artist_id).past_shows_count += 1
      Venue.query.get(venue_id).past_shows_count += 1

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
