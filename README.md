# Portale Gestione Volontari Buttrio

A basic activity management system developed for the Civil Protection ("Protezione Civile" in Italy) volunteers of my municipality. Based on Flask.

## Installation

### Cloning the repo

```text
git clone https://github.com/aquaino/pgv-buttrio.git
```

### Install dependencies

Create a virtual environment with:

```text
python -m venv .venv
```

Install project dependencies with:

```text
pip install -r requirements.txt
```

### Configure the database

This app is configured to work with PostgreSQL.

Create a database with:

```text
CREATE DATABASE [database];
CREATE USER [user] WITH ENCRYPTED PASSWORD '[password]';
GRANT ALL PRIVILEGES ON DATABASE [database] TO [user];
```

Duplicate the ```.env.example``` file in a new ```.env``` file. Overwrite the settings with something like this, using the newly created database credentials.

```text
SECRET_KEY = "[key]"
APP_SETTINGS = "app.config.DevelopmentConfig"
SQLALCHEMY_DATABASE_URI = "postgresql://[user]:[password]@localhost/[database]"
```

### Populate the database

Initialize the database using:

```text
flask recreate-db
```

Fill it with some example data, including an admin user to login with:

```text
flask setup-db
```

## Run the app

Finally, run the application using:

```text
flask run
```

And login to the system (at [http://localhost:5000](http://localhost:5000)) with:

- admin@admin.it
- admin
