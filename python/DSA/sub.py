library = {}
# add books 
def add_book():
    title = input("enter the title : ").strip()
    author = input("enter the author name: " ).strip()
    edition = int(input("enter the edition of that book: "))
    
    try:
        number = int(input("enter the number of book you want to store: "))
    except ValueError:
        print("invalid input!")
        return 
    
    key = (title.lower(), author.lower())

    if key in library:
        library[key][number] += number
        print(f'total books of author {author} has {number} copies')
    else:
        library[key] = {
            "title": title,
            "author": author,
            "edition": edition,
            "copies": number
            }
        

def search():
    bookName = input(" enter the book title to get: ").strip().lower()
    found = False
    for key , books in library.items():
        if bookName in key[0] or bookName in key[1]:
            print(f'book title: {books['title']}\n book author: {books['author']}\n number of books available: {books['number']}')  
            found = True
    if not found:
            print( "oops!, Book not found")
    
def view():
    if  not library:
        print("library is empty.")
        return
    print("viewing library------->")
    for books in library.values():
        print(f'* book title --> {books['title']}\n book author name --> {books['author']}\n total number of books --> {books['number']}')

def main():
    while True:
        print("---------------library menu--------------\n")
        print("1 - view books---->")
        print("2 - search for books---->")
        print("3 - add books---->")
        print("4 - exit---->")
        choice = input("choose number between 1-4 according your need: ").strip()

        if choice == "1":
            view()
        elif choice =="2":
            search()
        elif choice == "3":
            add_book()
        elif choice == "4":
            print("----------Exiting from library---------")
            break
        else:
            print("oops!, something gone wrong...")
    
if __name__ == "__main__":
    main()
        
