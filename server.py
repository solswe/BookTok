from flask import Flask, render_template,request, url_for, jsonify, json, redirect, session

import requests
import db
import sys
import os

# auth imports
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

# Load .env file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Get the key from .env
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

# Get NYT api key from .env
NYT_API_KEY = os.environ['NYT_API_KEY']


app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# Operates when accessing the URL for the first time
@app.before_first_request
def initialize():
  db.setup()

# ======== Auth Stuff ===========
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
  
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# ===== End of Auth Stuff ========


# Just added basic routes
@app.route('/', methods = ['GET','POST'] )
def home():
  bookshelves = 0
  bookshelves_length = 0

  # Check if user is logged in
  if session.get('user') is not None:
    # Get user's email address
    user_session = session.get('user')
    user_info = user_session['userinfo']
    user_email = user_info['email']

    # get a users bookshelf data
    data = db.get_user_bookshelves(user_email)
    bookshelves = []

    for data in data:
      bookshelves.append(data[0])

    bookshelves_length = len(bookshelves)
    print(bookshelves_length)


   # Get the value of the form when the user clicked the button
  if request.method == 'POST':
    for key, value in request.form.items():
      if key == 'romance':
        genres = key
      elif key == 'thriller':
        genres = key
      elif key == 'nonfiction':
        genres = key
      elif key == 'horror':
        genres = key
      elif key == 'comedy':
        genres = key
      else:
        genres = 'children'
    
    request_url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{genres}&maxResults=12&key={GOOGLE_API_KEY}'
    response = requests.get(request_url).json()
    items_length = len(response['items'])
    book_title = []
    author_names = []
    book_thumbnails = []
    book_published_dates = []
    book_isbn13 = []

    for i in range(items_length):
      book_title.append(response['items'][i]['volumeInfo']['title'])
      author_names.append(response['items'][i]['volumeInfo']['authors'][0])
      book_published_dates.append(response['items'][i]['volumeInfo']['publishedDate'])
      book_isbn13.append(response['items'][i]['volumeInfo']['industryIdentifiers'][0]['identifier'])

    # check if imageLinks is defined before appending to book_thumbnails
      if 'imageLinks' in response['items'][i]['volumeInfo']:
          book_thumbnails.append(response['items'][i]['volumeInfo']['imageLinks']['thumbnail'])
      else:
          book_thumbnails.append(None)

    try:
      genres = getattr(sys.modules[__name__], genres)
      
      return genres(bookshelves, bookshelves_length, book_title, author_names, book_thumbnails, book_published_dates, items_length, book_isbn13)

    except AttributeError:
      pass

  # If the method is ['GET] then just call NYT best seller
  else:
    
    # Requests NYT Bestseller 'combined print and ebook fiction' list (there's a lot of lists we can request)
    request_url = f"https://api.nytimes.com/svc/books/v3/lists/current/Combined%20Print%20and%20E-Book%20Fiction.json?api-key={NYT_API_KEY}"
    request_headers = {
      "Accept": "application/json"
    }
    response = requests.get(request_url, headers=request_headers)
    # print(response.text)

    # Turn json into a python dictionary
    response_dict = json.loads(response.text)

    # Get only book list info from response_dict
    book_dict = response_dict["results"]["books"]

    # Arrays that will hold featured list data (title, author, cover url)
    featured_title = []
    featured_author = []
    featured_cover = []
    featured_isbn13 = []

    # Get only necessary data for featured list from book_dict
    for i in book_dict:
      featured_title.append(i["title"])
      featured_author.append(i["author"])
      featured_cover.append(i["book_image"])    
      featured_isbn13.append(i['isbns'][0]['isbn13'])
     
      length = len(featured_title)

    # Send featured list data to home.html
    # json.dump is just for debugging can be deleted later
    return render_template('Home.html', bookshelves = bookshelves,
                                        bookshelves_length = bookshelves_length,
                                        cover_url = featured_cover, 
                                        featured_title = featured_title, 
                                        featured_author = featured_author,
                                        featured_isbn13 = featured_isbn13,
                                        length = length,
                                        session = session.get('user'), 
                                        pretty=json.dumps(session.get('user'), indent=4))

@app.route('/account')
def account():
  return render_template('Account.html', session = session.get('user'))

# @app.route('/genres')
# def Genres():
#   return render_template('genres.html', session = session.get('user'))

@app.route('/romance')
def romance(bookshelves, bookshelves_length, book_title, author_names, book_thumbnails, book_published_dates, items_length, book_isbn13):

  return render_template('Romance.html',bookshelves = bookshelves,
                                        bookshelves_length = bookshelves_length,
                                        romance_title = book_title,
                                        author_names = author_names,
                                        book_thumbnails = book_thumbnails,
                                        book_published_dates = book_published_dates,
                                        items_length = items_length,
                                        book_isbn13 = book_isbn13,
                                        session = session.get('user'))

@app.route('/thriller')
def thriller(bookshelves, bookshelves_length, book_title, author_names, book_thumbnails, book_published_dates, items_length, book_isbn13):
  
  return render_template('Thriller.html', bookshelves = bookshelves,
                                          bookshelves_length = bookshelves_length,
                                          thriller_title = book_title,
                                          author_names = author_names,
                                          book_thumbnails = book_thumbnails,
                                          book_published_dates = book_published_dates,
                                          items_length = items_length,
                                          book_isbn13 = book_isbn13,
                                          session = session.get('user'))

@app.route('/nonfiction')
def nonfiction(bookshelves, bookshelves_length, book_title, author_names, book_thumbnails, book_published_dates, items_length, book_isbn13):
  
  return render_template('Nonfiction.html', bookshelves = bookshelves,
                                            bookshelves_length = bookshelves_length,
                                            nonfiction_title = book_title,
                                            author_names = author_names,
                                            book_thumbnails = book_thumbnails,
                                            book_published_dates = book_published_dates,
                                            items_length = items_length,
                                            book_isbn13 = book_isbn13,
                                            session = session.get('user'))

@app.route('/horror')
def horror(bookshelves, bookshelves_length, book_title, author_names, book_thumbnails, book_published_dates, items_length, book_isbn13):

  return render_template('Horror.html', bookshelves = bookshelves,
                                        bookshelves_length = bookshelves_length,
                                        horror_title = book_title,
                                        author_names = author_names,
                                        book_thumbnails = book_thumbnails,
                                        book_published_dates = book_published_dates,
                                        items_length = items_length,
                                        book_isbn13 = book_isbn13,
                                        session=session.get('user'))

@app.route('/childrens')
def children(bookshelves, bookshelves_length, book_title, author_names, book_thumbnails, book_published_dates, items_length, book_isbn13):

  return render_template('Childrens.html',  bookshelves = bookshelves,
                                            bookshelves_length = bookshelves_length,
                                            children_title = book_title,
                                            author_names = author_names,
                                            book_thumbnails = book_thumbnails,
                                            book_published_dates = book_published_dates,
                                            items_length = items_length,
                                            book_isbn13 = book_isbn13,
                                            session = session.get('user'))

@app.route('/comedy')
def comedy(bookshelves, bookshelves_length, book_title, author_names, book_thumbnails, book_published_dates, items_length, book_isbn13):

  return render_template('Comedy.html', bookshelves = bookshelves,
                                        bookshelves_length = bookshelves_length,
                                        comedy_title = book_title,
                                        author_names = author_names,
                                        book_thumbnails = book_thumbnails,
                                        book_published_dates = book_published_dates,
                                        items_length = items_length,
                                        book_isbn13 = book_isbn13,
                                        session = session.get('user'))

@app.route('/BookSearchList', methods = ['GET','POST'])
def book_search_list():
  bookshelves = 0
  bookshelves_length = 0
  
  # Check if user is logged in
  if session.get('user') is not None:
    # Get user's email address
    user_session = session.get('user')
    user_info = user_session['userinfo']
    user_email = user_info['email']

    # get a users bookshelf data
    data = db.get_user_bookshelves(user_email)
    bookshelves = []

    for data in data:
      bookshelves.append(data[0])

    bookshelves_length = len(bookshelves)
    # print(bookshelves_length)

  # This route method is almost 'POST' method 
  if request.method == 'POST':
  
    # Get the user input from the form
    title = request.form.get('book_title')

    # Changed URL format for fetching ..
    # (ex: Harry potter -> Harry+potter)
    url_book_title = title.replace(" ", "+")
  
    # This is already defaulted 10 (from Google Books Api), so we do not need to set max.
    # I have set the global variable GOOGLE_API_KEY from line 21. 

    url = f'https://www.googleapis.com/books/v1/volumes?q={url_book_title}&maxResults=12&key={GOOGLE_API_KEY}'
    response = requests.get(url).json()
    items_length = len(response['items'])

    book_title =[]
    author_names = []
    book_thumbnails = []
    book_published_dates = []
    book_isbn = []

    # Get the data from the json (title, authors, thumbnail,publishedDate)
    
    for i in range(items_length):
      book_title.append(response['items'][i]['volumeInfo'].get('title', ''))
      author_names.append(response['items'][i]['volumeInfo'].get('authors', [''])[0])
      book_thumbnails.append(response['items'][i]['volumeInfo'].get('imageLinks', {}).get('thumbnail', ''))
      book_published_dates.append(response['items'][i]['volumeInfo'].get('publishedDate', ''))
      try:
        book_isbn.append(response['items'][i]['volumeInfo']['industryIdentifiers'][0].get('identifier', ''))
      except:
        book_isbn.append('x')

  return render_template('BookSearchList.html', bookshelves = bookshelves,
                                                bookshelves_length = bookshelves_length,
                                                items_length=items_length,
                                                book_title = book_title,
                                                author_names = author_names,
                                                book_thumbnails = book_thumbnails,
                                                book_published_dates = book_published_dates,
                                                book_isbn = book_isbn,
                                                session = session.get('user'))

# ===============================================================================

@app.route('/bookshelf', methods = ['GET','POST'])
def book_shelf():
  if session.get('user') is None:
    return render_template('UserOnly.html', session = session.get('user'))

  else:
    # bookshelf search is not being used
    searched_bookshelf = False

    # Get user's email address
    user_session = session.get('user')
    user_info = user_session['userinfo']
    user_email = user_info['email']

    with db.get_db_cursor(True) as cur:
      # Get user's bookshelf list
      cur.execute("SELECT bookshelfname FROM userinfo WHERE useremail = %s;", (user_email,))
      rows = cur.fetchall()
      bookshelves = []
      for row in rows:
        bookshelves.append(row[0])
      
      # Get list of shelved books
      books = []
      for bookshelf in bookshelves:
        cur.execute("SELECT bookTitle FROM shelvedbooks WHERE useremail = %s AND bookshelfname = %s;", (user_email, bookshelf,))
        temp = [row for row in cur.fetchall()]
        books.append(temp)
    
    if request.method == 'GET':
      return render_template('Bookshelf.html', session=session.get('user'),
                                               bookshelves=bookshelves,
                                               books=books,
                                               searched_bookshelf = searched_bookshelf)

    else:
      # POST request = when user searched user's bookshelf
      # The method of filtering is similar to the code directly above.
      # However this else statement is filtered by search_content by user's input

      # a bookshelf name is being searched for
      searched_bookshelf = True

      if request.form.get('book_shelf'):

        search_content = request.form.get('book_shelf')

        # get unique user emails w/ the bookshelf name searched
        user_bookshelf = db.select_user_info(search_content)
        unique_bookshelf_user = []
        
        for user_bookshelf in user_bookshelf:
          unique_bookshelf_user.append(user_bookshelf[0])

        # the books in each bookshelf retrieved from database
        books = []

        # for each user, get bookshelf (these bookshelves are all named the same thing)
        for i in unique_bookshelf_user:
          with db.get_db_cursor(commit=True) as cur:
            cur.execute("SELECT bookTitle FROM shelvedbooks WHERE useremail = %s AND bookshelfname = %s;", (i, search_content,))
            rows = cur.fetchall()
            books.append(rows)
         
        bookshelves = []
        with db.get_db_cursor(True) as cur:
          # Get user's bookshelf list
          cur.execute("SELECT bookshelfname FROM userinfo WHERE bookshelfname = %s;", (search_content,))
          bookshelf_data = cur.fetchall()
          for data in bookshelf_data:
            bookshelves.append(data[0])
     
        return render_template('Bookshelf.html',session=session.get('user'),
                                                bookshelves=bookshelves,
                                                books=books,
                                                searched_bookshelf = searched_bookshelf)
      
      else:
        # POST request = When user created new bookshelf

        # bookshelf search isn't being used
        searched_bookshelf = False

        # Get new bookshelf name
        new_bookshelf = request.form.get('bookshelfName')
        bookshelves.append(new_bookshelf)
        
        with db.get_db_cursor(True) as cur:
          # Create a bookshelf in database
          cur.execute("INSERT INTO userinfo(userEmail, bookshelfName) values (%s, %s);", (user_email, new_bookshelf,))
            
          # Render the HTML code for the newly created bookshelf
        return render_template('Bookshelf.html', session=session.get('user'),
                                                bookshelves=bookshelves,
                                                books=books,
                                                searched_bookshelf = searched_bookshelf)
    
@app.route('/delete/<bookshelf>', methods = ['POST'])
def delete_bookshelf(bookshelf):
  # Get user's email address
  user_session = session.get('user')
  user_info = user_session['userinfo']
  user_email = user_info['email']

  # Delete bookshelf from database
  with db.get_db_cursor(True) as cur:
    cur.execute("DELETE FROM userinfo WHERE userEmail = %s AND bookshelfName = %s;", (user_email, bookshelf,))
    cur.execute("DELETE FROM shelvedbooks WHERE userEmail = %s AND bookshelfName = %s;", (user_email, bookshelf,))

  return redirect(url_for('book_shelf'))


# Handel books doesn't have isbn
@app.route('/book/', methods = ['GET'])
def book_without_isbn():
  return render_template('UnidentifiedBook.html', session = session.get('user'))


@app.route('/book/<book_isbn>', methods = ['GET'])
def book_details(book_isbn):

  # Bring reviews for this book
  with db.get_db_cursor(True) as cur:
    cur.execute("SELECT review FROM managereviews WHERE isbn = %s;", (book_isbn,))
    rows = cur.fetchall()
    reviews = []
    for row in rows:
      reviews.append(row[0])

  if request.method == 'GET':

    url = f'https://www.googleapis.com/books/v1/volumes?q={book_isbn}&key={GOOGLE_API_KEY}'
    response = requests.get(url).json()

    if len(book_isbn) < 10:
      return render_template('UnidentifiedBook.html', session = session.get('user')) 
    
    # If book's isbn is valid
    try: 
      book_title = (response['items'][0]['volumeInfo'].get('title', ''))
      author_names = (response['items'][0]['volumeInfo'].get('authors', [''])[0])
      book_thumbnails = (response['items'][0]['volumeInfo'].get('imageLinks', {}).get('thumbnail', ''))
      book_published_dates = (response['items'][0]['volumeInfo'].get('publishedDate', ''))
      book_description = (response['items'][0]['volumeInfo'].get('description', ''))

      return render_template('Book.html', book_title = book_title,
                                          author_names = author_names,
                                          book_thumbnails = book_thumbnails,
                                          book_published_dates = book_published_dates,
                                          book_isbn = book_isbn,
                                          book_description=book_description,
                                          reviews=reviews,
                                          session = session.get('user'))
    
    # Some books doesn't have valid isbn
    except:
      return render_template('UnidentifiedBook.html', session = session.get('user'))
  
# Save submitted review in db
@app.route('/book/<book_isbn>', methods = ['POST'])
def add_review(book_isbn):
  submitted_review = request.form['newReview']

  with db.get_db_cursor(True) as cur:
    cur.execute("INSERT INTO managereviews(isbn, review) values (%s, %s);", (book_isbn, submitted_review,))

  return redirect(url_for('book_details', book_isbn=book_isbn))


# add a featured book to your bookshelf
@app.route('/add_featured_book', methods = ['POST'])
def add_featured_book():

  # get the bookshelf that was selected
  bookshelf_name = request.form.get('bookshelf_name')
  
  # if no bookshelf has been selected do nothing
  if(bookshelf_name == ''):
    print('Book was not added to any bookshelves.')
    return {"random": "data1"}
  
  # if a legit bookshelf has been selected, continue...
  else:
    # get user's email address
    user_session = session.get('user')
    user_info = user_session['userinfo']
    user_email = user_info['email']

    # get book isbn/book title data
    book_isbn13 = request.form.get('isbn13')
    book_title = request.form.get('book_title')

    # check if book is already in user's bookshelf (no duplicates allowed)
    # if everything is good, send data to database
    book_in_bookshelf_status = db.check_bookshelf_for_book(user_email, bookshelf_name, book_isbn13, book_title)
   
    print(book_in_bookshelf_status)
    # db.add_book_to_bookshelf(user_email, bookshelf_name, book_isbn13, book_title)
    return jsonify(status = book_in_bookshelf_status)

if __name__ == '__main__':

  # Added for debugging 
  app.run(debug=True)
  # If this is not working then, try this...
  # flask --app server.py --debug run
