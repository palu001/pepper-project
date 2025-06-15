import sqlite3
import os

class CinemaDatabase(object):
    def __init__(self, project_path):
        self.db_path = os.path.join(project_path, "data/cinema.db")

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def initialize_database(self):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            age_group TEXT,
            preferences TEXT,
            visit_count INTEGER DEFAULT 1
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            title TEXT,
            genre TEXT,
            duration INTEGER,
            rating TEXT,
            description TEXT,
            poster_url TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS showtimes (
            id INTEGER PRIMARY KEY,
            movie_id INTEGER,
            screen_number INTEGER,
            show_time TEXT,
            available_seats INTEGER,
            price REAL,
            FOREIGN KEY (movie_id) REFERENCES movies (id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS concessions (
            id INTEGER PRIMARY KEY,
            item_name TEXT,
            category TEXT,
            price REAL,
            description TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            showtime_id INTEGER,
            num_tickets INTEGER DEFAULT 1,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (showtime_id) REFERENCES showtimes(id)
        )
        ''')

        self.insert_sample_data(cursor)
        conn.commit()
        conn.close()

    def register_customer(self, name, age_group, genre):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM customers WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE customers SET visit_count = visit_count + 1, preferences = ? WHERE name = ?", (genre, name))
        else:
            cursor.execute("INSERT INTO customers (name, age_group, preferences, visit_count) VALUES (?, ?, ?, 1)",
                        (name, age_group, genre))
        conn.commit()
        conn.close()

    def update_customer_preferences(self, name, genre):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE customers SET preferences = ? WHERE name = ?", (genre, name))
        conn.commit()
        conn.close()

    def get_movies_by_genre(self, genre):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT title, description FROM movies WHERE genre = ?", (genre,))
        movies = cursor.fetchall()
        conn.close()
        return movies

    def get_recommendations_by_age(self, age_group):
        conn = self._connect()
        cursor = conn.cursor()
        if age_group == "child":
            cursor.execute("SELECT title, description FROM movies WHERE rating IN ('G', 'PG')")
        elif age_group == "teen":
            cursor.execute("SELECT title, description FROM movies WHERE rating IN ('PG', 'PG-13')")
        else:
            cursor.execute("SELECT title, description FROM movies")
        movies = cursor.fetchall()
        conn.close()
        return movies

    def get_showtimes_for_movie(self, movie_title):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.show_time, s.screen_number, s.available_seats, s.price
            FROM showtimes s
            JOIN movies m ON s.movie_id = m.id
            WHERE m.title = ?
        ''', (movie_title,))
        showtimes = cursor.fetchall()
        conn.close()
        return showtimes

    def get_description_for_movie(self, movie_title):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.description
            FROM movies m
            WHERE m.title = ?
        ''', (movie_title,))
        description = cursor.fetchall()
        conn.close()
        return description
    
    def get_screen_for_movie(self, title):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.screen_number
            FROM showtimes s
            JOIN movies m ON s.movie_id = m.id
            WHERE m.title = ?
        ''', (title,))
        result = cursor.fetchone()
        return result[0] if result else None


    def get_concessions(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, price, category FROM concessions")
        items = cursor.fetchall()
        conn.close()
        return items

    def insert_sample_data(self, cursor):
        """Insert sample cinema data"""
        movies = [
            (1, "The Amazing Adventure", "action", 120, "PG-13", "An epic journey of heroes", "poster1.jpg"),
            (2, "Love in Paris", "romance", 105, "PG", "A romantic comedy in the city of love", "poster2.jpg"),
            (3, "Space Warriors", "sci-fi", 140, "PG-13", "Battle for the galaxy", "poster3.jpg"),
            (4, "The Mystery House", "horror", 95, "R", "A spine-chilling thriller", "poster4.jpg"),
            (5, "Family Fun Time", "comedy", 90, "G", "Perfect for the whole family", "poster5.jpg")
        ]
        cursor.executemany('INSERT OR REPLACE INTO movies VALUES (?,?,?,?,?,?,?)', movies)

        showtimes = [
            (1, 1, 1, "14:00", 45, 12.50),
            (2, 1, 1, "17:00", 30, 12.50),
            (3, 1, 1, "20:00", 15, 15.00),
            (4, 2, 2, "15:30", 60, 12.50),
            (5, 2, 2, "18:30", 40, 15.00),
            (6, 3, 3, "16:00", 25, 15.00),
            (7, 3, 3, "19:30", 10, 15.00),
            (8, 4, 4, "21:00", 35, 15.00),
            (9, 5, 5, "13:00", 80, 10.00),
            (10, 5, 5, "15:00", 70, 10.00)
        ]
        cursor.executemany('INSERT OR REPLACE INTO showtimes VALUES (?,?,?,?,?,?)', showtimes)

        concessions = [
            (1, "Popcorn Large", "Snacks", 8.50, "Freshly popped with butter"),
            (2, "Soda Large", "Drinks", 6.00, "Various flavors available"),
            (3, "Nachos", "Snacks", 7.50, "With cheese sauce"),
            (4, "Candy Mix", "Snacks", 4.50, "Assorted movie theater candy"),
            (5, "Hot Dog", "Food", 9.00, "All-beef hot dog with toppings")
        ]
        cursor.executemany('INSERT OR REPLACE INTO concessions VALUES (?,?,?,?,?)', concessions)
    

    def get_customer_by_name(self, name):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT name, age_group, preferences FROM customers WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        return result

    def book_showtime(self, customer_name, movie_title, show_time):
        conn = self._connect()
        cursor = conn.cursor()

        # Trova ID cliente
        cursor.execute("SELECT id FROM customers WHERE name = ?", (customer_name,))
        customer = cursor.fetchone()
        if not customer:
            conn.close()
            raise ValueError("Cliente non trovato")
        customer_id = customer[0]

        # Trova ID spettacolo
        cursor.execute('''
            SELECT s.id
            FROM showtimes s
            JOIN movies m ON s.movie_id = m.id
            WHERE m.title = ? AND s.show_time = ?
        ''', (movie_title, show_time))
        showtime_id = cursor.fetchone()[0]
    
        print("showtime_id relativo a: ",movie_title, show_time," e: ",showtime_id)
        if not showtime_id:
            conn.close()
            raise ValueError("Spettacolo non trovato")
        

        # Registra prenotazione
        cursor.execute('''
            INSERT INTO bookings (customer_id, showtime_id)
            VALUES (?, ?)
        ''', (customer_id, showtime_id))

        conn.commit()
        conn.close()


    def get_all_movies(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM movies")
        movies = cursor.fetchall()
        conn.close()
        return movies
