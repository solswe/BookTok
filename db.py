""" database access
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""

from contextlib import contextmanager
import logging
import os

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None


def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    current_app.logger.info(f"creating db connection pool")
    pool = ThreadedConnectionPool(1, 4, dsn=DATABASE_URL, sslmode='require')


@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
      cursor = connection.cursor(cursor_factory=DictCursor)
      # cursor = connection.cursor()
      try:
          yield cursor
          if commit:
              connection.commit()
      finally:
          cursor.close()

def add_book_to_bookshelf (user_email, bookshelf_name, isbn13, book_title):
    with get_db_cursor(True) as cur:
        cur.execute("INSERT INTO shelvedbooks (userEmail, bookshelfName, isbn, bookTitle) values (%s, %s, %s, %s)", (user_email, bookshelf_name, isbn13, book_title,))


def get_user_bookshelves(user_email):
    with get_db_cursor(False) as cur:
        cur.execute("SELECT bookshelfname FROM userinfo WHERE useremail = %s;", (user_email,))
        return cur.fetchall()
    
def check_bookshelf_for_book(user_email, bookshelf_name, isbn13, book_title):
    with get_db_cursor(True) as cur:
        cur.execute("SELECT * FROM shelvedbooks WHERE userEmail = %s AND bookshelfName = %s AND isbn = %s;", (user_email, bookshelf_name, isbn13,))
        if cur.fetchone() is None:
            # not found - add book to shelf
            cur.execute("INSERT INTO shelvedbooks (userEmail, bookshelfName, isbn, bookTitle) values (%s, %s, %s, %s)", (user_email, bookshelf_name, isbn13, book_title,))
            return False
        else:
            return True
        
def select_user_info(bookshelf):
    with get_db_cursor(True) as cur:
        cur.execute("SELECT userEmail FROM userinfo WHERE bookshelfName = %s;", (bookshelf,))
        return cur.fetchall()