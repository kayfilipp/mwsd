# MWSD: This Message Will Self Destruct
an app that auto-deletes messages, keeps them safe, and lets users create
burner accounts to message each other through the command line.

## Features

 - **auto-expiring messages** : messages are destroyed from db once received by a user. 
 - **universal sessions for users** : users can only be logged into one session at a time to prevent malicious actors from using your credentials to read messages.
 - **riddle capability** : users can agree on a statement-answer combination required to unlock incoming messages. Any messages unlocked incorrectly are also immediately deleted.
 - **Burners Everywhere** : All users, messages, and sessions expire eventually, reducing bloat and maximizing privacy.

## Coming Soon

 - **User and Message permanence** : Users with a paid RapidAPI key create permanent user accounts and allow message persistence for longer periods.
 - **Discoverability** : Users can list themselves publicly on the MWSD exchange to be found by other users.

## Demo - Python
Creating a user is as easy as sending a `POST` request.

```python
import requests as r 
user = {
    "username": "arctic-monkey",
    "password": "doIwannaKnow25"
}

r.post("https://www.mwsd.com/api/user/register", json=user)
```

### Sending a Message with no pass phrase
Checking messages or sending a new messages requires a session, which can be created after you make a new user (or an existing one).

```python
token = r.post("https://www.mwsd.com/api/sesion/create", json=user).json()

message = {
    "message": {
        "to_username": "portgualTheMan",
        "body": "i'm atomic man!"
    },
    "session_validate": token
}

r.post("https://www.mwsd.com/api/message/send", json=message)
```

### Sending a Message with a pass phrase 
If you're relaying highly sensitive data and have high trust with the other party, you can hide a message behind 
a pass phrase - the user will see a `statement` phrase and must respond to it with an appropriate `answer` to 
get the message. Otherwise, they get gibberish.

```python
message = {
    "message": {
        "to_username": "portgualTheMan",
        "body": "i'm atomic man!",
        "statement": "where is karate?", # what the user sees when they try to read the message 
        "answer": "never in here." # what the user must answer to see the full body
    },
    "session_validate": token
}

r.post("https://www.mwsd.com/api/message/send", json=message)
```

### Checking Your Inbox
```python
messages = r.get("https:/www.mwsd.com/api/message/all", json=token).json()
```

```json
[
    {
        'id': 41, 
        'from_username': 'someguy123', 
        'to_username': 'fkrasovsky', 
        'sent_on': '2025-06-18T08:27:10.349718', 
        'expires_on': '2025-06-23T08:27:10.351276', 
        'is_locked': true, 
        'statement': 'what is the capital of st kitts and nevis?'
    }
]
```

messages with `is_locked` = `True` are hidden behind a `statement` that must be answered correctly. Usually, this phrase is agreed upon by two high-trust parties before the message is sent.

otherwise, a message can simply be opened by running its ID through the `read` or `answer` endpoint.

### Reading Messages, Locked & Unlocked
```python
# is_locked = true 
answer_message = r.post(
    f"https://www.mwsd.com/api/message/41/answer", 
    json=token,
    params={"answer": "bassettere"}
)
```

If your answer corresponds to the answer designated by the sender, you will see the full body of the message. Otherwise, the server responds with a `200` containing complete gibberish. This is mostly done to fool bots.

```python
# is_locked = False 
read_message = r.get(
    "https://www.mwsd.com/api/message/42/read",
    json=token
)

"""
200, this is a message.
"""
```

Attempting to read a locked message will return a `423: LOCKED` response with a preview of the message and what endpoint it can be accessed through.
Any message that is successfully read is immediately deleted from storage, so make sure to keep local copies as needed.


# Running Your Own MWSD Server


## Setup
Download relevant packages with

`pip install -r requirements.txt`

## Running
this app is best launched through uvicorn:

```bash 
uvicorn app:app --reload
```

## Accessing PG in WSL:
```bash
sudo -u postgres psql

# necessary perms 
GRANT ALL PRIVILEGES ON SCHEMA public TO your_user;
GRANT CREATE ON SCHEMA public TO your_user;
```

### Schema Changes - Alembic
This app uses Alembic for migrating changes in db schema.
You can create a new alembic instance by running:

```bash
alembic init alembic
```
This will create `alembic.ini` and an `alembic` directory.
Update your `.ini` file with an updated `sqlalchemy.url` - this can be `SQLite`, `PostgreSQL`, etc.

**If you are using a PostgreSQL database with a SQLModel ORM**
Update `alembic/env.py` with the following configuration:

```python
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from sqlmodel import SQLModel
from sqlalchemy import engine_from_config, pool
from alembic import context

# all models go here
from models.user import User
from models.foo import Foo

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata
```

Alembic will not manage any models not included in this `env` file.

```bash
alembic revision --autogenerate -m "Add New Object"
alembic upgrade head
```

This will create a new migration that updates your database.
This app use `Postgresql` as a backend. but you can configure your
database of choice


**Using WSL**

If executing these on a windows machine, you can use the Windows Subsystem for Linux (WSL):

```bash
wsl --install ubuntu
```

then, in a separate terminal:

```

```

### Task Scheduling using Celery / Celery Beat 
The `tasks.py` file contains a list of scheduled tasks that can be run on a routine basis.
This celery implementation uses `rabbitMQ` to manage queues. In order to launch the entire stack, run the 
following commands:

```bash
sudo systemctl start rabbitmq-server
python -m celery -A tasks worker --loglevel=INFO
celery -A tasks beat --loglevel=INFO
```