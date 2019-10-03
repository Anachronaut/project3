import re
import sqlite3

db_art = 'test_catalog.sqlite'
prev_injection = (";", "'", "--", "/*", "*/", "xp_")

def create_tables(): #creates artists and artwork tables
    try:
        with sqlite3.connect(db_art) as conn:
            conn.execute('PRAGMA foreign_keys = ON') #enables foreign keys
            conn.execute('CREATE TABLE IF NOT EXISTS artists (artist_ID integer PRIMARY KEY AUTOINCREMENT, name text NOT NULL, email text)')
            conn.execute('CREATE TABLE IF NOT EXISTS artwork (artwork_ID integer PRIMARY KEY AUTOINCREMENT, artist_name text NOT NULL, title text NOT NULL, price integer, status text NOT NULL, artists_ID integer NOT NULL, FOREIGN KEY(artists_ID) REFERENCES artists(artist_ID))')
    except sqlite3.Error as e:
        print(f'Error creating tables because {e}')
    finally:
        conn.close()

#***INPUT VALIDATION FUNCTIONS***
def valid_name(name): #artist name validation
    if re.match(r'([^\s\w]|_)+', name):
        print('String cannot contain special characters.')
        print()
        return True
    elif name.isnumeric():
        print('Input string cannot be entirely numeric.')
        print()
        return True
    elif name.isspace():
        print('Input string cannot be whitespace.')
        print()
        return True
    elif len(name) < 2:
        print('Input string needs to be longer than two characters.')
        print()
        return True
    else:
        return False

def valid_email(email): #artist email validation
    if any(char in email for char in prev_injection): #allows for special characters in e-mail, while preventing characters used for SQL injections
        print('Invalid characters in e-mail address.')
        print()
        return True
    elif email.isnumeric():
        print('Input string cannot be entirely numeric.')
        print()
        return True
    elif email.isspace():
        print('Input string cannot be whitespace.')
        print()
        return True
    elif len(email) < 7:
        print('Input string needs to be longer than seven characters.')
        print()
        return True
    else:
        return False

def valid_title(title): #artwork title validation
    if any(char in title for char in prev_injection): #allows for special characters in artwork title, while preventing characters used for SQL injections
        print("Invalid characters in artwork's title.")
        print()
        return True
    elif title.isspace():
        print('Input string cannot be whitespace.')
        print()
        return True
    else:
        return False

def valid_status(status): #availability status input validation
    status_list = ['AVAILABLE', 'SOLD']
    if status not in status_list:
        return True
    else:
        return False
#***END INPUT VALIDATION FUNCTIONS***


#***UI: INPUT FUNCTIONS***
def artist_name(): #Input Artist's Name
    while True:
        name = input("Enter the artist's name: ")
        name = name.upper()
        if valid_name(name):
            continue
        elif not valid_name(name):
            return name
            break

def artist_email(): #Input Artist's Email
    while True:
        email = input ("Enter the new artist's e-mail: ")
        if valid_email(email):
            continue
        elif not valid_email(email):
            return email
            break

def art_title(): #Input Artwork Title
    while True:
        title = input("Enter the title of the artwork: ")
        title = title.upper()
        if valid_title(title):
            continue
        elif not valid_title(title):
            return title
            break

def new_art_title(): #Check if new Artwork Title already exists
    while True:
        title = art_title()
        with sqlite3.connect(db_art) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM artwork WHERE title = ?', (title, )) #checks if title already exists for artwork in the artwork table
            artwork = cur.fetchone()
            if not artwork:
                return title
                break
            else:
                print()
                print('Artwork title already in database')
                print()
                continue

def art_status(): #Input Artwork Status
    while True:
        status = input("Is the artwork AVAILABLE or SOLD?: ")
        status = status.upper()
        if valid_status(status):
            print("Incorrect entry. Please enter 'AVAILABLE' or 'SOLD'")
            continue
        elif not valid_status(status):
            return status
            break

def art_price(): #Input Artwork Price
    while True:
        try:
            price = int(input("Enter the whole dollar price of the artwork in USD: $")) #Rounded numbers to make retrieval and sorting in sqlite easier
        except ValueError:
            print("Please enter a whole number")
            continue
        else:
            print()
            return price
            break

def delete_choice(title): #Input Delete Artwork Choice
    del_list = ['DELETE', 'CANCEL']
    while True:
        del_choice = input("Type DELETE to delete this artwork, ("+title+"), or type CANCEL to cancel the deletion: ")
        del_choice = del_choice.upper()
        if del_choice not in del_list: #input validation
            print("Incorrect entry. Please enter 'DELETE' or 'CANCEL'")
            continue
        else:
            return del_choice
            break

def change_choice(): #Input Artwork Availability Status Change Choice
    choice_list = ['Y','N']
    while True:
        chg_choice = input("Would you like to change the status? (Y/N): ")
        chg_choice = chg_choice.upper()
        print()
        if chg_choice not in choice_list:
            print("Invalid entry. Please enter 'Y' or 'N'")
            continue
        else:
            return chg_choice
            break
#***END UI: INPUT FUNCTIONS***



def select_art(artist_id, art_status1, art_status2): #selects either all (AVAILABLE & SOLD) or AVAILABLE artwork by artist_ID
    with sqlite3.connect(db_art) as conn:
        cur = conn.cursor()
        try:
            cur.execute('SELECT * FROM artwork WHERE artists_ID = ? AND (status = ? OR status = ?) ORDER BY artwork_ID ASC', (artist_id, art_status1, art_status2))
            #AVAILABLE, AVAIALABLE for available; AVAILABLE, SOLD for all
            artworks = cur.fetchall()
            print()
            for row in artworks:
                print(row)
            print()
        except sqlite3.Error:
            print('Error finding artworks')

def find_artist(name): #finds artist by name and returns their artist_ID from artists table
    with sqlite3.connect(db_art) as conn:
        cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM artists WHERE name = ?', (name, ))
        artist = cur.fetchone()
        artist_id = artist[0]
        if artist is not None:
            return artist_id
        elif artist is None:
            print("Artist not found")
            print()
    except sqlite3.Error:
        print('Error finding artist ID')


def find_indv_art(artist_id, title): #Finds individual artwork in artwork table by title, artists_ID
    with sqlite3.connect(db_art) as conn:
        cur = conn.cursor()
        print()
        while True:
            cur.execute('SELECT * FROM artwork WHERE title = ? AND artists_ID = ?', (title, artist_id))
            artwork = cur.fetchone()
            print()

            if artwork is not None:
                return artwork
                break
            else:
                print("Artwork not found")
                print()
                continue

def add_artist(name, email): #add artist to artists table
    name = name.upper()
    try:
        with sqlite3.connect(db_art) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM artists WHERE name = ? AND email = ?', (name, email)) #checks if entry alredy exists for artist in the artists table
            artist = cur.fetchall()
            if not artist:
                conn.execute('INSERT INTO artists(name, email) VALUES (?,?)', (name, email))
            else:
                print()
                print('Artist already in database')
                print()
    except sqlite3.Error as e:
        print(f'Error adding artist because {e}')
    finally:
        conn.close()

def add_artwork(name, title, status, price): #add new artwork to artwork table
    with sqlite3.connect(db_art) as conn:
        cur = conn.cursor()
        try:
            artist_id = find_artist(name)
            if artist_id is None:
                print()
                print("Artist not found, please add artist to database.")
                print()
                add_artist()
            else:
                cur.execute('SELECT * FROM artists WHERE artist_ID = ?', (artist_id, ))
                artist = cur.fetchone()
                name = artist[1]
        except sqlite3.Error:
            print("Artist error")

        try:
            conn.execute('INSERT INTO artwork(artist_name, title, price, status, artists_ID) VALUES (?,?,?,?,?)', (name, title, price, status, artist_id))
        except sqlite3.Error as e:
            print(f'Error adding artwork to artwork table: {e}')
        finally:
            conn.commit()

def delete_artwork(name, title): #delete individual artwork from artwork table by title, artists_ID
    with sqlite3.connect(db_art) as conn:
        try:
            artist_id = find_artist(name)
        except sqlite3.Error:
            print("Artist error")
        else:
            try:
                artwork = find_indv_art(artist_id, title)
                title = artwork[2]
                del_choice = delete_choice(title)
                if del_choice == 'CANCEL':
                    menu()
                elif del_choice == 'DELETE':
                    conn.execute('DELETE FROM artwork WHERE title = ? AND artists_ID = ?', (title, artist_id))
                    print()
                    print("ARTWORK DELETED")
                    print()
            except sqlite3.Error as e:
                print(f'Error deleting artwork because {e}')
            finally:
                conn.commit()

def change_status(name, title): #change status of individual artwork from artwork table to AVAILABLE or SOLD
    with sqlite3.connect(db_art) as conn:
        try:
            while True:
                artist_id = find_artist(name)
                if artist_id is None:
                    continue
                elif artist_id is not None:
                    break
        except sqlite3.Error:
            print("Artist error")
        else:
            try:
                artwork = find_indv_art(artist_id, title)
                title = artwork[2]
                status = artwork[4]
                print("Artwork is currently:", status)
                print()
                chg_choice = change_choice()
                if chg_choice == 'N':
                    menu()
                elif chg_choice == 'Y': #checks current status and changes to opposite
                    if status == 'AVAILABLE':
                        new_status = 'SOLD'
                    elif status == 'SOLD':
                        new_status = 'AVAILABLE'
                conn.execute('UPDATE artwork SET status = ? WHERE title = ? AND artists_ID = ?', (new_status, title, artist_id))
                print('Status changed to:', new_status)
            except sqlite3.Error:
                print("Error updating status")
            finally:
                conn.commit()


def menu():
    while True:
        print()
        print("ARTWORK DATABASE MENU")
        print('-'*40)
        print("(1) - Add a new artist")
        print("(2) - Display all art by artist")
        print("(3) - Display available art by artist")
        print("(4) - Add new artwork")
        print("(5) - Delete artwork")
        print("(6) - Update artwork availability")
        print('-'*40)
        print()
        choice = input('Please choose an option, type Q to quit: ')
        if len(choice) > 1:
            print('Invalid entry')
            continue
        elif choice == '1':
            print()
            name = artist_name()
            email = artist_email()
            add_artist(name, email)
        elif choice == '2':
            print()
            name = artist_name()
            artist_id = find_artist(name)
            select_art(artist_id, 'AVAILABLE', 'SOLD')
        elif choice == '3':
            print()
            name = artist_name()
            artist_id = find_artist(name)
            select_art(artist_id, 'AVAILABLE', 'AVAILABLE')
        elif choice == '4':
            print()
            name = artist_name()
            title = new_art_title()
            status = art_status()
            price = art_price()
            add_artwork(name, title, status, price)
        elif choice == '5':
            print()
            name = artist_name()
            title = art_title()
            delete_artwork(name, title)
        elif choice == '6':
            print()
            name = artist_name()
            title = art_title()
            change_status(name, title)
        elif choice == 'Q' or choice == 'q':
            quit()
        else:
            continue

def main():
        menu()

create_tables()
main()
