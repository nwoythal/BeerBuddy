# BeerBuddy
BeerBuddy is meant for those who enjoy beer. It consists of a few key components:
* SQLite3 backend, "BeerSchema.db"
* Flask/SQLAlchemy frontend
    * BeerBuddy.py
    * *.html
## Setup
1. Install python/pip
    * (preferably python3, I have not tested against 2)
1. `bash setup_env.sh`
    * Creates virtual environment under BeerBuddy/static/env
    * Installs all pip dependencies.
    * You may need to point to where the virtual environment is with:`. ./BeerBuddy/static/env/bin/activate`
1. `flask run` in the directory with BeerBuddy.py
    * Server default is localhost:5000

## Layout and design choices:
I made a few conscious design choices when constructing the groundwork for BB. First, no chain breweries. This means places like CB Potts, BJ's, Rock Bottom, etc. will not make it onto the list, as they would violate the setup for the DB, i.e. a beer in the beer table would need multiple entries for its brewery_id, thus I would have to create an index or something of that nature.

I also (albeit unknowingly) opted to not include RBAC stuff when creating the database in sqlite3. This means that in the future, to allow users to post beers or breweries or even verify reviews, I would probably need to migrate to MySQL or something that supports user accounts.
### ERD
![Beer_ERD](https://github.com/nwoythal/BeerBuddy/blob/master/Beer_ERD_Final.png)

## Future improvements
I would like to allow more user-end integration with the website, but as stated in the layout section, I would need to completely overhaul my database backend to allow a more intuitive and safe UX. It would also probably be beneficial to put more data in the backend. Adding CSS to make everything pretty would also be a plus.
