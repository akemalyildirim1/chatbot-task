# chatbot-task

## Table of contents
* [General Informations](#general-informations)
* [Installation](#installation)
* [How To Run It?](#how-to-run-it)


## General Informations:

The core backend application for task.

## Installation

Make sure that you have installed Poetry with Python 3.12.

Activate the virtual environment of Poetry:
```bash
poetry shell
```

To install dependencies of the project:
```bash
poetry install
```

## How To Run It?

### Environment Variables

Before running application and migrations, you need to export environment variables.

The variables that you need to export are listed:

```
SQL_DB__HOST=localhost
SQL_DB__PORT=5432
SQL_DB__USER=dbuser
SQL_DB__PASSWORD=dbpass
SQL_DB__NAME=postgres
VECTOR_DB__HOST=localhost
VECTOR_DB__KEY=secret-db-key
DROPBOX__CLIENT_ID=dropbox-client-id
DROPBOX__CLIENT_SECRET=dropbox-client-secret
DROPBOX__REDIRECT_URI=http://localhost:8000/dropbox/login/callback/
COHERE_API_KEY=cohere-api-key
```

### Migrations

After exporting environment variables,

Run

```bash
alembic upgrade head
```

### Api

Run

```bash
uvicorn src.main:app --reload
```

or

```bash
make run
```
