
function add_book(id, shelf_name, book_title) {
    console.log("adding book...");
    // console.log(id);
    // console.log(shelf_name);
    // console.log(book_title);

    if(shelf_name != "") {
        let data = new FormData()
        data.append("isbn13", id)
        data.append("bookshelf_name", shelf_name)
        data.append("book_title", book_title)

        fetch('/add_featured_book', {
            "method": "POST",
            "body": data,
        })
        .then((response) => response.json())
        .then((data) => {
            console.log('Success:', data);
            console.log(data.status);

            // book is already in shelf so it can't be added
            if(data.status == true) {
                document.getElementById('status_' + id).innerHTML = "<p>Book exists in bookshelf.</p>";
                setTimeout(time, 2000, id);
            }
            // book isn't in shelf yet so it was added
            else {
                document.getElementById('status_' + id).innerHTML = "<p>Book added to bookshelf.</p>";
                setTimeout(time, 2000, id);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}

function time(id) {
    console.log("timeout is working...")
    console.log("status_" + id);
    document.getElementById('status_' + id).innerHTML = "";
}
