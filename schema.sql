-- Created
CREATE TABLE userinfo (
    userEmail varchar not null,
    bookshelfName varchar not null
);

CREATE TABLE shelvedBooks (
  userEmail varchar not null,
  bookshelfName varchar not null,
  isbn varchar(20) not null,
  bookTitle varchar not null
);

CREATE TABLE manageReviews (
  isbn varchar(20) not null,
  review varchar not null
);

insert into userinfo(useremail, bookshelfname) values ('kim01540@umn.edu', '');

insert into shelvedbooks(useremail, bookshelfname, isbn, booktitle) values ('kim01540@umn.edu', 
                                                                            'my mystery books', 
                                                                            '', 
                                                                            '');

-- \dt             : (print out table )
-- \d (table name) : (print out table info)
drop table Book;
SELECT * from Book;

-- delete data from table
TRUNCATE TABLE  table_name;

