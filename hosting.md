
# Running Your Own MWSD Server
The MWSD standard can be launched by anyone from any server.
This guide explains a basic approach to hosting your own MWSD service.

## Tech Stack
FastAPI (Backend)<br>
PostgreSQL (Storage)<br>
Render.com (Hosting)<br>
Alembic (Migrations)<br>
Celery (Background Tasks)

## Setup - Render
1. Make an account with <a href="https://dashboard.render.com/">Render</a>.

2. Create a new project and provision a Postgres database. Make sure to save the connection string as you'll need to provide it in the config later.

3. In the same project, create a new web service. You can attach this web service to the github repo that hosts your MWSD code. The build commands will include a `pip install` of any requirements you need.

4. Update the Start command to `uvicorn app:app --host 0.0.0.0 --port $PORT`

5. in Settings, make sure to update the following environment variables, either by hand or from your  `.env` file:

```python
# pg sql url from step 2 goes here - internal or external URl is fine
PG_URL="postgresql://yourpgsql_url@localhost/mwsd"

# this is for running integrations tests on your server, optional
APP_URL = "http://127.0.0.1:8000"

# USER SESSION EXTENSIONS 
STANDARD_EXPIRES_IN_HRS = 1 # how long sessions last
STANDARD_EXTENSION_HRS = 1  # how much sessions get extended by

# MESSAGE EXPIRATION
STANDARD_MESSAGE_EXPIRES_IN_HRS = 120
```

After this, you can deploy your app service.

## Setup - Alembic
Our data models need to be migrated to our new database, for which we can use `Alembic` by running the following command.

```bash
alembic init alembic
```

This creates an `alembic` folder and an `alembic.ini` file. 

1. Modify your `.ini` file by supplying the `sqlalchemy.url` value, which is just the connection string that you saved earlier after making your postgres DB.

2. Modify the `alembic/env.py` file to include the following imports:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlmodel import SQLModel
from sqlalchemy import engine_from_config, pool
from alembic import context
from models.user import User
from models.user_session import UserSession
from models.message import Message

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata
```

If you want to migrate additional SQL Models, make sure to include them in this file by importing them.

3. Modify `alembic/script.py.mako` to include the following imports:

```python
import sqlalchemy as sa
import sqlmodel
```

4. Run the following db migration:

```bash
alembic revision --autogenerate -m "Add New SQL Objects"
alembic upgrade head
```

**You should run step 4 every time you make changes to any of your ORM/SQL Models in `models/`. Changes to the Base model or any objects with `Table=True` need to be migrated.**


### Setup - Task Scheduling using Celery / Celery Beat 
The `tasks.py` file contains a list of scheduled tasks that can be run on a routine basis.
This celery implementation uses `rabbitMQ` to manage queues. In order to launch the entire stack, run the 
following commands:

```bash
rabbitmq-server start -detached
python -m celery -A tasks worker --loglevel=INFO
celery -A tasks beat --loglevel=INFO
```

### Setup - Task Scheduling using Render's Task Service

Because Render's shells for web services are highly restrictive, it may be best to abandon using `celery` and make a series of normal python tasks instead, running them via Render's <a href="https://dashboard.render.com/cron/new">CRON Service</a>.