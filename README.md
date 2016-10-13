# Watchdog
Watchdog is a stock simulation application that is meant to be very basic.
Its end goal is to offer basic buy/sell features, limited information on stocks, and a competitive leaderboard.
#### TODO: Switch DB backend from SQLite3 to Postgres.
## Requirements
### System Requirements
`virtualenv`

`Python 2.7`

`Django 1.10`

See the `requirements.txt` file for what is installed in the virtualenv.

## Setup
Clone the repository. Then, `cd` into the parent directory. To enter the virtual environment, run `source ase/bin/activate`
and make sure you run `./manage.py migrate` to configure your, initial DB.

Next, run `./manage.py runserver` to start the application. 

## Development and Testing
Refer to the exceptionally detailed [Django documentation](https://docs.djangoproject.com/) for most questions.

We will be following PEP8 standards. We will use `flake8` to lint our application.

To test, we will use `mock` and `case` to simulate function calls and make comparative assertions.

