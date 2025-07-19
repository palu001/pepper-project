import sqlite3
import os
import numpy as np
from classes.rotate_model_tf import RotatEModel
import tensorflow as tf 
from collections import Counter, defaultdict
from classes.recommendation_dataset import KGBuilder
import random

class CinemaDatabase(object):
    def __init__(self, project_path):
        self.db_path = os.path.join(project_path, "data/cinema.db")
        self.builder=KGBuilder()
        random.seed(42)
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
            description TEXT DEFAULT 'description not available' ,
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
            price REAL DEFAULT 5,
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
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,           
            feedback_status TEXT DEFAULT 'not_rated', -- 'not_rated' or 'rated'
            liked_movie BOOLEAN, -- True if liked, False if disliked           
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (showtime_id) REFERENCES showtimes(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            concession_id INTEGER,
            quantity INTEGER DEFAULT 0,
            UNIQUE (customer_id, concession_id),
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (concession_id) REFERENCES concessions(id)
        )
        ''')

        self.insert_sample_data(cursor)
        self.load_from_kg_and_populate(cursor=cursor, conn=conn) 
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
            cursor.execute("SELECT MAX(id) FROM customers")
            max_id = cursor.fetchone()[0]
            next_id = max(6040, max_id if max_id else 6040) + 1

            # Insert new customer with next_id
            cursor.execute(
                "INSERT INTO customers (id, name, age_group, preferences, visit_count) VALUES (?, ?, ?, ?, 1)",
                (next_id, name, age_group, genre)
            )
        conn.commit()
        conn.close()

    def get_movies_by_genre(self, genre):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT m.title, m.description
            FROM movies m
            JOIN showtimes s ON m.id = s.movie_id
            WHERE m.genre = ?
        """, (genre,))
        movies = cursor.fetchall()
        conn.close()
        return movies

    def get_recommendations_by_age(self, age_group):
        conn = self._connect()
        cursor = conn.cursor()
        if age_group == "child":
            cursor.execute("""
                SELECT DISTINCT m.title, m.description
                FROM movies m
                JOIN showtimes s ON m.id = s.movie_id
                WHERE m.rating IN ('G', 'PG')
            """)
        elif age_group == "teen":
            cursor.execute("""
                SELECT DISTINCT m.title, m.description
                FROM movies m
                JOIN showtimes s ON m.id = s.movie_id
                WHERE m.rating IN ('PG', 'PG-13')
            """)
        else:
            cursor.execute("""
                SELECT DISTINCT m.title, m.description
                FROM movies m
                JOIN showtimes s ON m.id = s.movie_id
            """)
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

    def get_concession_item(self, item_name):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM concessions WHERE item_name = ?", (item_name,))
        item = cursor.fetchone()
        conn.close()
        print("my item is: ", item)
        return item

    def insert_sample_data(self, cursor):
        """Insert sample cinema data"""
        movies = [
            (50000, "The Amazing Adventure", "action", 120, "PG-13", "An epic journey of heroes", "poster1.jpg"),
            (50001, "Love in Paris", "romance", 105, "PG", "A romantic comedy in the city of love", "poster2.jpg"),
            (50002, "Space Warriors", "sci-fi", 140, "PG-13", "Battle for the galaxy", "poster3.jpg"),
            (50003, "The Mystery House", "horror", 95, "R", "A spine-chilling thriller", "poster4.jpg"),
            (50004, "Family Fun Time", "comedy", 90, "G", "Perfect for the whole family", "poster5.jpg")
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
        cursor.execute("SELECT id, name, age_group, preferences FROM customers WHERE name = ?", (name,))
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

    def place_concession_order_list(self, customer_name, item_list):
        """
        item_list: lista di stringhe, ciascuna rappresenta un item_name
        """
        conn = self._connect()
        cursor = conn.cursor()
        # Trova ID cliente
        cursor.execute("SELECT id FROM customers WHERE name = ?", (customer_name,))
        customer = cursor.fetchone()
        if not customer:
            conn.close()
            raise ValueError("Cliente non trovato")
            print("cliente non trovato")
        customer_id = customer[0]

        # Conta occorrenze di ciascun item nella lista
        from collections import Counter
        item_counts = Counter(item_list)  # esempio: {'Popcorn Large': 2, 'Hot Dog': 1}

        for item_name, count in item_counts.items():
            # Trova ID del prodotto
            cursor.execute("SELECT id FROM concessions WHERE item_name = ?", (item_name,))
            concession = cursor.fetchone()
            if not concession:
                continue  # ignora item non valido
            concession_id = concession[0]

            # Inserisci o aggiorna quantita
            cursor.execute('''
                SELECT quantity FROM orders WHERE customer_id = ? AND concession_id = ?
            ''', (customer_id, concession_id))
            row = cursor.fetchone()

            if row:
                cursor.execute('''
                    UPDATE orders
                    SET quantity = quantity + ?
                    WHERE customer_id = ? AND concession_id = ?
                ''', (count, customer_id, concession_id))
            else:
                cursor.execute('''
                    INSERT INTO orders (customer_id, concession_id, quantity)
                    VALUES (?, ?, ?)
                ''', (customer_id, concession_id, count))
            
        conn.commit()
        conn.close()




    def get_most_ordered_concession(self, customer_name):
        conn = self._connect()
        cursor = conn.cursor()

        # Trova ID cliente
        cursor.execute("SELECT id FROM customers WHERE name = ?", (customer_name,))
        customer = cursor.fetchone()
        if not customer:
            conn.close()
            raise ValueError("Cliente non trovato")
        customer_id = customer[0]

        # Recupera l'item piu ordinato
        cursor.execute('''
            SELECT c.item_name, o.quantity
            FROM orders o
            JOIN concessions c ON o.concession_id = c.id
            WHERE o.customer_id = ?
            ORDER BY o.quantity DESC
            LIMIT 1
        ''', (customer_id,))
        
        most_ordered = cursor.fetchone()
        conn.close()

        return most_ordered  # restituisce (item_name, quantity) oppure None


    def get_unrated_movie_for_customer(self, customer_name):
            """
            Finds the most recent movie a customer booked but hasn't rated yet.
            Returns the movie title if found, otherwise None.
            """
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.title, s.show_time, s.screen_number
                FROM bookings b
                JOIN customers c ON b.customer_id = c.id
                JOIN showtimes s ON b.showtime_id = s.id
                JOIN movies m ON s.movie_id = m.id
                WHERE c.name = ? AND b.feedback_status = 'not_rated'
                ORDER BY b.booking_date DESC
                LIMIT 1
            ''', (customer_name,))
            result = cursor.fetchone()
            conn.close()
            return result if result else None
    
    def record_movie_feedback(self, customer_name, movie_title, liked_status):
        """
        Records a customer's feedback for a specific movie, marking it as 'rated'.
        """
        conn = self._connect()
        cursor = conn.cursor()
        # Find the latest unrated booking for this movie and customer
        cursor.execute('''
            UPDATE bookings
            SET feedback_status = 'rated', liked_movie = ?
            WHERE id = (
                SELECT b.id FROM bookings b
                JOIN customers c ON b.customer_id = c.id
                JOIN showtimes s ON b.showtime_id = s.id
                JOIN movies m ON s.movie_id = m.id
                WHERE c.name = ? AND m.title = ? AND b.feedback_status = 'not_rated'
                ORDER BY b.booking_date DESC
                LIMIT 1
            )
        ''', (1 if liked_status=='True' else 0, customer_name, movie_title))
        conn.commit()
        conn.close()

    def get_liked_movie_count(self, customer_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM bookings
            WHERE customer_id = ? AND liked_movie = 1
        ''', (customer_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count


    def get_movie_details(self, movie_title):
        """Retrieves all details for a specific movie, like its genre."""
        conn = self._connect()
        conn.row_factory = sqlite3.Row # Allows accessing columns by name
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movies WHERE title = ?", (movie_title,))
        details = cursor.fetchone()
        conn.close()
        return dict(details) if details else None
    
    def get_available_showtime_titles(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT m.title
            FROM showtimes s
            JOIN movies m ON s.movie_id = m.id
            WHERE s.available_seats > 0
        ''')
        results = cursor.fetchall()
        conn.close()
        return [r[0] for r in results]
        
    def get_movie_titles_by_ids(self, movie_ids):
        if not movie_ids:
            return []

        conn = self._connect()
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in movie_ids)
        query = "SELECT title FROM movies WHERE id IN ({})".format(placeholders)
        cursor.execute(query, movie_ids)
        results = cursor.fetchall()
        conn.close()

        return [row[0] for row in results]

    def get_booked_movie_ids_by_user(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT s.movie_id
            FROM bookings b
            JOIN showtimes s ON b.showtime_id = s.id
            WHERE b.customer_id = ?
        ''', (user_id,))
        result = [row[0] for row in cursor.fetchall()]
        conn.close()
        return result
    

    
    def retrain_model(self):
        from classes.train_and_eval import train_rotate  # Assuming your training script is named like this
        train_rotate()

    def append_feedback_to_kg(self, user_name, movie_title):
        conn = self._connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM customers WHERE name = ?", (user_name,))
        user_row = cursor.fetchone()
        cursor.execute("SELECT id FROM movies WHERE title = ?", (movie_title,))
        movie_row = cursor.fetchone()
        conn.close()

        if not user_row or not movie_row:
            print("User or movie not found")
            return

        user_id, movie_id = user_row[0], movie_row[0]
        user_str = "user_{}".format(user_id)
        movie_str = "movie_{}".format(movie_id)
        new_triple = "{}\tlikes\t{}\n".format(user_str,movie_str)

        with open("data/train.txt", "a") as f:
            f.write(new_triple)
        with open("data/kg.txt", "a") as f:
            f.write(new_triple)






    
    def build_vocab(self,files):
        entity2id, relation2id = {}, {}
        eid = 0
        rid = 0
        for file in files:
            with open(file) as f:
                for line in f:
                    h, r, t = line.strip().split("\t")
                    if h not in entity2id:
                        entity2id[h] = eid
                        eid += 1
                    if t not in entity2id:
                        entity2id[t] = eid
                        eid += 1
                    if r not in relation2id:
                        relation2id[r] = rid
                        rid += 1
        return entity2id, relation2id

    def load_model_and_recommend(self, username):
        entity2id, relation2id = self.build_vocab(["data/kg.txt"])
        id2entity = {v: k for k, v in entity2id.items()}
        user_id=self.get_customer_by_name(username)[0]
        booked_movie_ids = self.get_booked_movie_ids_by_user(user_id)
        booked_entity_ids = {"movie_{}".format(mid) for mid in booked_movie_ids}

        model = RotatEModel(num_entities=len(entity2id), num_relations=len(relation2id), embedding_dim=10)
        saver = model.get_saver()

        with tf.Session() as sess:
            saver.restore(sess, "checkpoints/rotate_model.ckpt")
            print("Model loaded from checkpoint.")

            top_movie_ids = self.recommend_top_k("user_{}".format(user_id), model, sess, entity2id, relation2id, id2entity, 3500)
            # Extract movie numeric IDs (e.g., movie_23 -> 23)
            # Filter out movies already booked
            unseen_movie_ids = [mid for mid in top_movie_ids if mid not in booked_entity_ids]

            movie_ids = [int(mid.split("_")[1]) for mid in unseen_movie_ids if mid.startswith("movie_")]
            titles=self.get_movie_titles_by_ids(movie_ids)
            return titles

   
    def recommend_top_k(self, user_str, model, sess, entity2id, relation2id, id2entity, k=3500):
        user_id = entity2id.get(user_str)
        relation_id = relation2id.get("likes")
        movie_ids = [eid for ent, eid in entity2id.items() if ent.startswith("movie_")]


        scores = model.get_score_op(sess, user_id, relation_id, movie_ids)
        top_indices = np.argsort(scores)[-k:][::-1]
        top_movie_ids = [movie_ids[i] for i in top_indices]
        return [id2entity[mid] for mid in top_movie_ids]


    def load_from_kg_and_populate(self, user_to_add="user_6", cursor=None, conn=None):
        # Determine if we need to create a new connection or use an existing one
        _close_conn = False
        if conn is None or cursor is None:
            conn = self._connect()
            cursor = conn.cursor()
            _close_conn = True # Flag to close connection at the end if we opened it
        # Load KG
        kg_triples = self.builder.load_kg_file()
        movie_likes = [triple for triple in kg_triples if triple[1] == "likes"]

        # Build movie genres from KG
        genre_map = {}
        for subj, pred, obj in kg_triples:
            if pred == "is_genre":
                movie_id = subj  # e.g., "movie_123"
                genre = obj.replace("genre_", "").replace("_", " ")
                genre_map[movie_id] = genre

        # Count likes per movie
        movie_like_counts = {}
        for _, _, movie in movie_likes:
            movie_like_counts[movie] = movie_like_counts.get(movie, 0) + 1

        # Load movie titles from file
        movie_titles = {}
        with open(self.builder.movies_file, 'r') as f:
            for line in f:
                parts = line.strip().split("::")
                if len(parts) >= 3:
                    movie_id, title, _ = parts
                    movie_titles["movie_" + movie_id] = title


        # Insert top 100 most liked movies
        top_movies = sorted(movie_like_counts.items(), key=lambda x: x[1], reverse=True)[:300]
        inserted_movies = []

        for movie_uri, _ in top_movies:
            title = movie_titles.get(movie_uri)
            genre = genre_map.get(movie_uri)
            # Ensure Unicode
            if isinstance(title, bytes):
                title = title.decode('latin-1')

            if isinstance(genre, bytes):
                 genre = genre.decode('latin-1')

            cursor.execute('''
                INSERT INTO movies (id,title, genre, duration, rating, poster_url)
                VALUES (?, ?, ?, NULL, NULL, NULL)
            ''', (int(movie_uri.split("_")[1]),title, genre))
            inserted_movies.append((cursor.lastrowid, movie_uri))  # Save DB id and URI

        conn.commit()

        # Step 3: Add one user from KG
        user_age = None
        for subj, pred, obj in kg_triples:
            if subj == user_to_add and pred == "has_age":
                user_age = obj.replace("agegroup_", "")
                break
        user_numeric_id = int(user_to_add.split('_')[-1])
        user_name="franco"
        cursor.execute('''
            INSERT INTO customers (id, name, age_group, preferences, visit_count)
            VALUES (?, ?, ?, NULL, 1)
        ''', (user_numeric_id,user_name, user_age))
        user_db_id = cursor.lastrowid

        # Get all movies the user likes
        liked_movies = [triple[2] for triple in movie_likes if triple[0] == user_to_add]

        for movie_uri in liked_movies:
            title = movie_titles.get(movie_uri)
            genre = genre_map.get(movie_uri)

            # Check if already inserted
            cursor.execute("SELECT id FROM movies WHERE title = ?", (title,))
            row = cursor.fetchone()
            if row:
                movie_id = row[0]
            else:
                cursor.execute('''
                    INSERT INTO movies (title, genre, duration, rating, description, poster_url)
                    VALUES (?, ?, NULL, NULL, NULL, NULL)
                ''', (title, genre))
                movie_id = cursor.lastrowid
                inserted_movies.append((movie_id, movie_uri))

            # Add booking (with liked_movie = True)
            cursor.execute('''
                INSERT INTO bookings (customer_id, showtime_id, num_tickets, liked_movie)
                VALUES (?, NULL, 1, 1)
            ''', (user_db_id,))

        conn.commit()

        # Step 4: Add 50 showtimes with non-overlapping random times
        used_times = set()
        count = 0
        random.shuffle(inserted_movies) 
        for movie_id, _ in inserted_movies:
            if count >= 50:
                break

            # Find available time and screen combo
            for _ in range(100):  # limit attempts
                hour = random.randint(15, 21)
                minute = random.choice([0, 30])
                show_time = "%02d:%02d" % (hour, minute)
                screen = random.randint(1, 5)

                if (screen, show_time) not in used_times:
                    used_times.add((screen, show_time))
                    break

            cursor.execute('''
                INSERT INTO showtimes (movie_id, screen_number, show_time, available_seats, price)
                VALUES (?, ?, ?, ?, ?)
            ''', (movie_id, screen, show_time, 50, 10.0))
            count += 1

        if _close_conn: # Only commit and close if we opened the connection
            conn.commit()
            conn.close()