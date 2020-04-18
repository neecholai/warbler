# Warbler

## About the application

This repo contains an app called Warbler (deployed on Heroku). 

In order to make requests to the backend, a user be registered and logged in to receive a JWT for authentication.

two apps, a create-react-app (deployed with Netlify) for the front-end and a Node API (deployed on Heroku) for the backend. We're using Netlify Identity for managing user information/authentication.

In order to make *any* requests to the backend, a header called "X-App-Data" must be sent to the server with a valid JWT signed from the create-react-app. What this is means is that you can not use Insomnia to test any routes without passing in a valid JWT. In development, the secret key is just the string "secret" so you can create your own token at JWT.io for testing purposes.

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

