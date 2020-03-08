# SCAS Client Texting Service

A web app that programatically follows up with clients within a specified time frame!


## Quickstart

### Local development

This project is built using the [Flask](http://flask.pocoo.org/) web framework. It runs on Python 2.7+ and Python 3.4+.

To run the app locally, first clone this repository and `cd` into its directory. Then:

1. Create a new virtual environment with Python 2.7:
    - If using vanilla [virtualenv](https://virtualenv.pypa.io/en/latest/):

        ```bash
        $ virtualenv -p /usr/bin/python2.7 venv
        $ source venv/bin/activate
        ```

    - If using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/):

        ```bash
        $ mkvirtualenv appointment-reminders
        ```

1. Install the requirements:

    ```bash
    $ pip install -r requirements.txt
    ```

1. Start a local PostgreSQL database and create a database called `clients`:
    - If on a Mac, we recommend [Postgres.app](http://postgresapp.com/). After install, open psql and run `CREATE DATABASE clients;`
    - If Postgres is already installed locally, you can just run `createdb clients` from a terminal

1. Copy the `.env_example` file to `.env`, and edit it to include your credentials for the Twilio API (found at https://www.twilio.com/user/account/voice) and your local Postgres database
1. Run `source .env` to apply the environment variables (or even better, use [autoenv](https://github.com/kennethreitz/autoenv))

1. Run the migrations with:

    ```bash
    $ alembic upgrade +1
    ```
    Note: If you have a local postgres installation where you access without password add this line to your `pg_hba.conf` file, *JUST FOR DEVELOPMENT, DO NOT USE THIS IN PRODUCTION*:
    `host    all             YOUR_USER         127.0.0.1/32            trust`

1. Start a [redis](http://redis.io/) server to be our Celery broker. If on a Mac, we recommend installing redis through [homebrew](http://brew.sh/)

1. Start the development server:

    ```bash
    $ python runapp.py
    ```

You can now access the application at
[http://localhost:5000](http://localhost:5000). To send any reminders, however,
you must also start a separate Celery worker process.


1. Start a new terminal session, `cd` into the repository, and active your
   `appointment-reminders` virtualenv

1. Start the Celery worker:

    ```bash
    $ celery -A reminders.celery worker -l info
    ```

Celery will now send SMS reminders for any new appointments you create through
the web app.

## Run the tests

You can run the tests locally through [pytest](http://pytest.org/).

Follow the instructions in the [Local Development](#local-development) section above, and then run:

```bash
$ py.test --cov tests
```

You can then view the results with `coverage report` or build an HTML report with `coverage html`.

## Meta

* No warranty expressed or implied. Software is as is. Diggity.
* [MIT License](http://www.opensource.org/licenses/mit-license.html)
* This repo was built based off of the Twilio [appointment reminders tutorial](https://www.twilio.com/docs/tutorials/walkthrough/appointment-reminders/python/flask)
