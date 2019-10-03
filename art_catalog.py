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
        print(artist)
        if artist is not None:
            return artist
        elif artist is None:
            print("Artist not found")
            print()
    except sqlite3.Error:
        print('Error finding artist ID')

def confirm_artist(): #confirms artist exists
    try:
        while True:
            print()
            name = input("Please enter the name of the artist: ")
            name = name.upper()
            print()
            if valid_name(name):
                continue
            elif not valid_name(name):
                break
            artist = find_artist(name)
            artist_id = artist[0]
            if artist_id is None:
                print("Artist not found")
                print()
                continue
            else:
                break
    except sqlite3.Error:
        print("Error finding artist")
    else:
        return name

def find_art(art_status1, art_status2): #finds all or AVAILABLE art by artist name
    print()
    name = input("Enter the artist's name: ")
    name = name.upper()
    try:
        artist = find_artist(name)
        artist_id = artist[0]
    except sqlite3.Error:
        print('Error finding artist')
    else:
        select_art(artist_id, art_status1, art_status2)

def find_indv_art(artist_id): #Finds individual artwork in artwork table by title, artists_ID
    with sqlite3.connect(db_art) as conn:
        cur = conn.cursor()
        print()
        while True:
            title = input("Please enter the title of the artwork: ")
            title = title.upper()
            if valid_title(title):
                continue
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

def add_artist(): #add artist to artists table
    print()
    try:
        while True:
            name = input("Enter the new artist's name: ")
            name = name.upper()
            if valid_name(name):
                continue
            elif not valid_name(name):
                break

        while True:
            email = input ("Enter the new artist's e-mail: ")
            if valid_email(email):
                continue
            elif not valid_email(email):
                break

    except sqlite3.Error:
        print("Artist entry error")

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

def add_artwork(): #add new artwork to artwork table
    print()
    name = input("Enter the name of the artist you would like to add Artwork for: ")
    name = name.upper()
    with sqlite3.connect(db_art) as conn:
        cur = conn.cursor()
        try:
            artist_id = find_artist(name)
            if artist_id is None:
                print()
                print("Artist not found, please add artist to database.")
                print()
                add_artist()
        except sqlite3.Error:
            print("Artist error")
        else:
            try:

                while True:
                    print()
                    title = input("Enter the title of the artwork: ")
                    title = title.upper()
                    if valid_title(title):
                        continue
                    elif not valid_title(title):
                        print()
                        break

                while True:
                    try:
                        price = int(input("Enter the whole dollar price of the artwork in USD: $")) #Rounded numbers to make retrieval and sorting in sqlite easier
                    except ValueError:
                        print("Please enter a whole number")
                        continue
                    else:
                        print()
                        break

                while True:
                    status = input("Is the artwork AVAILABLE or SOLD?: ")
                    status = status.upper()
                    if valid_status(status):
                        print("Incorrect entry. Please enter 'AVAILABLE' or 'SOLD'")
                        continue
                    elif not valid_status(status):
                        break

                conn.execute('INSERT INTO artwork(artist_name, title, price, status, artists_ID) VALUES (?,?,?,?,?)', (name, title, price, status, artist_id))
            except sqlite3.Error as e:
                print(f'Error adding artwork to artwork table: {e}')
            finally:
                conn.commit()

def delete_artwork(): #delete individual artwork from artwork table by title, artists_ID
    del_list = ['DELETE', 'CANCEL']
    with sqlite3.connect(db_art) as conn:
        try:
            name = confirm_artist()
            artist_id = find_artist(name)
        except sqlite3.Error:
            print("Artist error")
        else:
            try:
                artwork = find_indv_art(artist_id)
                title = artwork[2]
                while True:
                    del_choice = input("Type DELETE to delete this artwork, ("+title+"), or type CANCEL to cancel the deletion: ")
                    del_choice = del_choice.upper()
                    if del_choice not in del_list: #input validation
                        print("Incorrect entry. Please enter 'DELETE' or 'CANCEL'")
                        continue
                    else:
                        break
                if del_choice == 'CANCEL':
                    menu()
                elif del_choice == 'DELETE':
                    conn.execute('DELETE FROM artwork WHERE title = ? AND artists_ID = ?', (title, artist_id))
                    print()
                    print("ARTWORK DELETED")
                    print()
            except sqlite3.Error:
                print("Error deleting artwork")
            finally:
                conn.commit()

def change_status(): #change status of individual artwork from artwork table to AVAILABLE or SOLD
    with sqlite3.connect(db_art) as conn:
        try:
            while True:
                name = confirm_artist()
                artist = find_artist(name)
                if artist is None:
                    continue
                elif artist is not None:
                    artist_id = artist[0]
                    break
        except sqlite3.Error:
            print("Artist error")
        else:
            try:
                artwork = find_indv_art(artist_id)
                title = artwork[2]
                status = artwork[4]
                print("Artwork is currently:", status)
                print()
                while True:
                    chg_choice = input("Would you like to change the status? (Y/N): ")
                    chg_choice = chg_choice.upper()
                    print()
                    if chg_choice == 'N':
                        menu()
                    elif chg_choice == 'Y': #checks current status and changes to opposite
                        if status == 'AVAILABLE':
                            new_status = 'SOLD'
                            break
                        elif status == 'SOLD':
                            new_status = 'AVAILABLE'
                            break
                    else:
                        print()
                        print("Incorrect entry. Please enter 'Y' or 'N'")
                        continue
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
        print('-'*35)
        print("(1) - Add a new artist")
        print("(2) - Display all art by artist")
        print("(3) - Display available art by artist")
        print("(4) - Add new artwork")
        print("(5) - Delete artwork")
        print("(6) - Update artwork availability")
        print('-'*35)
        print()
        choice = input('Please choose an option, type Q to quit: ')
        if len(choice) > 1:
            print('Invalid entry')
            continue
        elif choice == '1':
            add_artist()
        elif choice == '2':
            find_art('AVAILABLE', 'SOLD')
        elif choice == '3':
            find_art('AVAILABLE', 'AVAILABLE')
        elif choice == '4':
            add_artwork()
        elif choice == '5':
            delete_artwork()
        elif choice == '6':
            change_status()
        elif choice == 'Q' or choice == 'q':
            quit()
        else:
            continue

def main():
        menu()

create_tables()
main()
