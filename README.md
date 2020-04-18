# Warbler

## About the application

This repo contains an app called Warbler (deployed on Heroku). 

Warbler is a twitter clone. Warbler allows users to post bite-sized thoughts and find and follow other users. Users can share and like other contributers' 'warbles' and search contributers in the database to find new friends or people to follow.

In order to make requests to the backend, a user be registered and logged in to receive a JWT for authentication.

## Technologies Used

- Javascript
- Python
- Flask
- SQL 
- SQL Alchemy
- Jinja2
- Bcrypt
- WTForms

## Getting Started 

### Create the Python virtual environment:
`$ python3 -m venv venv`
`$ source venv/bin/activate`

### Install requirements
`(venv) $ pip install -r requirements.txt`

### Set up the database:
`(venv) $ createdb warbler`
`(venv) $ python seed.py`

### Start the server:
`(venv) $ flask run`

### Deployed 
The staging api app is live on heroku at: 
https://nicholaihanse-warbler.herokuapp.com

