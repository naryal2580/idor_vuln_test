#!/usr/bin/env python3


from fastapi import FastAPI, HTTPException
from faker import Faker
from random import randint
import sqlite3
import os
import uvicorn


fake = Faker()
api = FastAPI()
max_id = randint(randint(1111, 9999), randint(11111, 99999))
db_name = './database.db'


def add_entry(db, _id, name, address, email):
    db.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (
        int(_id),
        str(name),
        str(address),
        str(email)
        )
    )
    db.commit()


@api.on_event("startup")
def startup_event():
    if not os.path.isfile(db_name):
        db = sqlite3.connect(db_name)
        db.execute('''
CREATE TABLE users (
id PRIMARY_KEY,
name TEXT,
address TEXT,
email TEXT
)
        '''[1:-1].strip())
        db.commit()
        add_entry(0, 'Anonymous', 'Your network', 'some_fake_email_placeholder@protonmail.com')


@api.get('/')
def root():
    return {'resp': 'Hey, check /docs for some juice!'}


@api.get('/user_info')
def user_info(id: int):

    if id > max_id:
        raise HTTPException(
                            status_code=404,
                            detail='Entry not found.'
                        )

    db = sqlite3.connect(db_name)
    ids = tuple(db.execute('SELECT id FROM users'))
    if ids.count((id,)):
        entry = tuple(db.execute('SELECT * FROM users WHERE id=:_id', {'_id': id}))[0]
        resp = {
                'id': entry[0],
                'name': entry[1],
                'address': entry[2],
                'email': entry[3]
            }
    else:
        name, addr, email = fake.name(), fake.address(), fake.email()
        add_entry(db, id, name, addr, email)
        resp = {
                'id': id,
                'name': name,
                'address': addr,
                'email': email
            }

    return {'resp': resp}


@api.get('/last_id')
def return_last_id():
    return {'last_id': max_id}


@api.get('/reset_id')
def reset_id():
    global max_id
    max_id = randint(randint(1111, 9999), randint(11111, 99999))
    return {'status': True}


@api.get('/custom_id')
def reset_to_custom_id(id: int):
    global max_id
    max_id = id
    return {'status': True}


if __name__ == '__main__':
    uvicorn.run("main:api", port=3117, reload=True)
