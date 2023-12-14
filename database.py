import os
import sqlite3

import pandas as pd
from dotenv import load_dotenv
from peewee import SqliteDatabase, Model, CharField, TextField

load_dotenv()

DB_FILE = os.getenv("DB_FILE")
local_db = SqliteDatabase(DB_FILE)


class BaseModel(Model):
    """A base model that linked to sqlite db."""

    class Meta:
        database = local_db


class Post(BaseModel):
    """A model to store posts."""

    id = CharField(unique=True, primary_key=True)
    link = CharField()
    date_gmt = CharField()
    title = TextField()
    summary = TextField()
    content = TextField()
    category = CharField(null=True)
    post_tags = CharField(null=True)
    syndication = CharField(null=True)


def init():
    """Initialize the database."""

    # delete local_db file if it exists
    if os.path.exists(DB_FILE):
        print(f"Deleting {DB_FILE}...")
        os.remove(DB_FILE)

    # create tables
    local_db.create_tables([Post])
    print("New DB created!")


def load_sqlite_as_df(file: str = DB_FILE, table: str = "post") -> pd.DataFrame:
    """Get a dataframe of the posts."""
    with sqlite3.connect(file) as conn:
        return pd.read_sql_query(f"SELECT * FROM {table}", conn)
