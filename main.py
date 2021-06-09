#!/usr/bin/env python3


from fastapi import FastAPI, HTTPException
from faker import Faker
from random import randint
import aiosqlite
import os
import uvicorn
from signal import SIGKILL


fake = Faker()
api = FastAPI()
max_id = randint(randint(1111, 9999), randint(11111, 99999))
db_name = './database.db'


async def add_entry(db, _id, name, address, email):
    await db.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (
        int(_id),
        str(name),
        str(address),
        str(email)
        )
    )
    await db.commit()


@api.on_event("startup")
async def startup_event():
    if not os.path.isfile(db_name):
        db = await aiosqlite.connect(db_name)
        await db.execute('''
CREATE TABLE users (
id PRIMARY_KEY,
name TEXT,
address TEXT,
email TEXT
)
        '''[1:-1].strip())
        await db.commit()
        await add_entry(db, 0, 'Anonymous', 'Your network', 'some_fake_email_placeholder@protonmail.com')


@api.get('/')
def root():
    return {'resp': 'Hey, check /docs for some juice!'}


@api.get('/user_info')
async def user_info(id: int):

    if id > max_id:
        raise HTTPException(
                            status_code=404,
                            detail='Entry not found.'
                        )

    db = await aiosqlite.connect(db_name)
    ids_cur = await db.execute('SELECT id FROM users')
    ids = tuple(await ids_cur.fetchall())
    await ids_cur.close()

    if ids.count((id,)):
        entry_cur = await db.execute('SELECT * FROM users WHERE id=:_id', {'_id': id})
        entry = await entry_cur.fetchone()
        await entry_cur.close()
        resp = {
                'id': entry[0],
                'name': entry[1],
                'address': entry[2],
                'email': entry[3]
            }

    else:
        name, addr, email = fake.name(), fake.address(), fake.email()
        await add_entry(db, id, name, addr, email)
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


@api.on_event('shutdown')
def suicide():
    os.kill(os.getpid(), SIGKILL)


if __name__ == '__main__':
    uvicorn.run("main:api", port=3117)
