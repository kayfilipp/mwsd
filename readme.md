# MWSD: This Message Will Self Destruct
an app that auto-deletes messages, keeps them safe, and lets users create
burner accounts to message each other through the command line.

Read the full API Documentation <a href="https://mwsd.onrender.com/docs">here.</a>

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

r.post("https://mwsd.onrender.com/api/v1/user/register", json=user)
```

### Creating a Session 
Sessions are required to send, read, and answer messages. Each user may only have one active session at any time and must log out of it.
Sessions are always temporary and will disappear on their own unless they are extended. Sessions have a session hash that must be passed
to other endpoints to work properly.

```python
token = r.post("https://mwsd.onrender.com/api/v1/sesion/create", json=user).json()
```

### Sending a Message with no pass phrase
Checking messages or sending a new messages requires a session, which can be created after you make a new user (or an existing one).

```python
message = {
    "message": {
        "to_username": "portgualTheMan",
        "body": "im atomic man!"
    },
    "session_validate": token
}

r.post("https://mwsd.onrender.com/api/v1/message/send", json=message)
```

### Sending a Message with a pass phrase 
If you"re relaying highly sensitive data and have high trust with the other party, you can hide a message behind 
a pass phrase - the user will see a `statement` phrase and must respond to it with an appropriate `answer` to 
get the message. Otherwise, they get gibberish.

```python
message = {
    "message": {
        "to_username": "portgualTheMan",
        "body": "im atomic man!",
        "statement": "where is karate?", # what the user sees when they try to read the message 
        "answer": "never in here." # what the user must answer to see the full body
    },
    "session_validate": token
}

r.post("https://mwsd.onrender.com/api/v1/message/send", json=message)
```

### Checking Your Inbox
```python
messages = r.get("https:/www.mwsd.com/api/v1/message/all", json=token).json()
```

```json
[
    {
        "id": 41, 
        "from_username": "someguy123", 
        "to_username": "fkrasovsky", 
        "sent_on": "2025-06-18T08:27:10.349718", 
        "expires_on": "2025-06-23T08:27:10.351276", 
        "is_locked": true, 
        "statement": "what is the capital of st kitts and nevis?"
    }
]
```

messages with `is_locked` = `True` are hidden behind a `statement` that must be answered correctly. Usually, this phrase is agreed upon by two high-trust parties before the message is sent.

otherwise, a message can simply be opened by running its ID through the `read` or `answer` endpoint.

### Reading Messages, Locked & Unlocked
```python
# is_locked = true 
answer_message = r.post(
    f"https://mwsd.onrender.com/api/v1/message/41/answer", 
    json=token,
    params={"answer": "bassettere"}
)
```

If your answer corresponds to the answer designated by the sender, you will see the full body of the message. Otherwise, the server responds with a `200` containing complete gibberish. This is mostly done to fool bots.

```python
# is_locked = False 
read_message = r.get(
    "https://mwsd.onrender.com/api/v1/message/42/read",
    json=token
)

"""
200, this is a message.
"""
```

Attempting to read a locked message will return a `423: LOCKED` response with a preview of the message and what endpoint it can be accessed through.
Any message that is successfully read is immediately deleted from storage, so make sure to keep local copies as needed.

