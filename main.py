#!/usr/bin/env python
# -*- coding: utf-8 -*-

import qi
import argparse
import sys
import os
import sqlite3
import pandas as pd
import time
import json
from datetime import datetime, timedelta
from classes.motion_manager import *

# Global variables
project_path = None
ALMemory = None
ALDialog = None
tts_service = None
ALMotion = None
tablet_service = None
current_customer = None

def graceful_close(ALDialog, topic_name):
    """Gracefully close the dialog system"""
    print("\nTerminating Cinema Assistant...\n")
    ALDialog.unsubscribe('cinema_assistant')
    ALDialog.deactivateTopic(topic_name)
    ALDialog.unloadTopic(topic_name)
    return 0

def initialize_database():
    """Initialize the cinema database with movies, showtimes, and customer data"""
    conn = sqlite3.connect(os.path.join(project_path, "data/cinema.db"))
    cursor = conn.cursor()
    
    # Create tables
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
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age_group TEXT,
            preferences TEXT,
            visit_count INTEGER DEFAULT 1
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
    
    # Insert sample data
    insert_sample_data(cursor)
    conn.commit()
    conn.close()

def insert_sample_data(cursor):
    """Insert sample cinema data"""
    # Sample movies
    movies = [
        (1, "The Amazing Adventure", "action", 120, "PG-13", "An epic journey of heroes", "poster1.jpg"),
        (2, "Love in Paris", "romance", 105, "PG", "A romantic comedy in the city of love", "poster2.jpg"),
        (3, "Space Warriors", "sci-fi", 140, "PG-13", "Battle for the galaxy", "poster3.jpg"),
        (4, "The Mystery House", "horror", 95, "R", "A spine-chilling thriller", "poster4.jpg"),
        (5, "Family Fun Time", "comedy", 90, "G", "Perfect for the whole family", "poster5.jpg")
    ]
    
    cursor.executemany('INSERT OR REPLACE INTO movies VALUES (?,?,?,?,?,?,?)', movies)
    
    # Sample showtimes
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
    
    # Sample concessions
    concessions = [
        (1, "Popcorn Large", "Snacks", 8.50, "Freshly popped with butter"),
        (2, "Soda Large", "Drinks", 6.00, "Various flavors available"),
        (3, "Nachos", "Snacks", 7.50, "With cheese sauce"),
        (4, "Candy Mix", "Snacks", 4.50, "Assorted movie theater candy"),
        (5, "Hot Dog", "Food", 9.00, "All-beef hot dog with toppings")
    ]
    
    cursor.executemany('INSERT OR REPLACE INTO concessions VALUES (?,?,?,?,?)', concessions)

def get_movies_by_genre(genre):
    """Get movies filtered by genre"""
    conn = sqlite3.connect(os.path.join(project_path, "data/cinema.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT title, description FROM movies WHERE genre = ?", (genre,))
    movies = cursor.fetchall()
    conn.close()
    return movies

def get_showtimes_for_movie(movie_title):
    """Get showtimes for a specific movie"""
    conn = sqlite3.connect(os.path.join(project_path, "data/cinema.db"))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.show_time, s.screen_number, s.available_seats, s.price 
        FROM showtimes s 
        JOIN movies m ON s.movie_id = m.id 
        WHERE m.title = ?
    """, (movie_title,))
    showtimes = cursor.fetchall()
    conn.close()
    return showtimes

def get_recommendations_by_age(age_group):
    """Get movie recommendations based on age group"""
    conn = sqlite3.connect(os.path.join(project_path, "data/cinema.db"))
    cursor = conn.cursor()
    
    if age_group == "child":
        cursor.execute("SELECT title, description FROM movies WHERE rating IN ('G', 'PG')")
    elif age_group == "teen":
        cursor.execute("SELECT title, description FROM movies WHERE rating IN ('PG', 'PG-13')")
    else:  # adult
        cursor.execute("SELECT title, description FROM movies")
    
    movies = cursor.fetchall()
    conn.close()
    return movies

def show_tablet_content(content_type, data=None):
    """Display content on Pepper's tablet"""
    if tablet_service:
        if content_type == "movies":
            tablet_service.showWebview("file:///opt/aldebaran/www/movies.html")
        elif content_type == "showtimes":
            tablet_service.showWebview("file:///opt/aldebaran/www/showtimes.html")
        elif content_type == "map":
            tablet_service.showWebview("file:///opt/aldebaran/www/cinema_map.html")

def handle_cinema_functions(value):
    print("Handling cinema function", value)
    """Handle various cinema assistant functions"""
    global current_customer
    
    if value == "greet_customer":
        greeting_gesture()
        current_customer = {"interaction_start": datetime.now()}
        
    elif value == "check_movie_preference":
        print("Checking movie preference...")
        preference = ALMemory.getData("cinema/movie_preference")
        print("Customer preference:", preference)
        movies = get_movies_by_genre(preference)
        print("Movies found:", movies)
        if movies:
            movie_list = ", ".join([movie[0] for movie in movies[:3]])
            ALMemory.raiseEvent("cinema/movie_suggestions", movie_list)
            print("Suggested movies:", movie_list)
        
    elif value == "get_showtimes":
        movie_title = ALMemory.getData("cinema/selected_movie")
        showtimes = get_showtimes_for_movie(movie_title)
        if showtimes:
            time_list = ", ".join([showtime[0] for showtime in showtimes])
            ALMemory.raiseEvent("cinema/available_times", time_list)
            show_tablet_content("showtimes", showtimes)
            
    elif value == "age_recommendations":
        age_group = ALMemory.getData("cinema/age_group")
        movies = get_recommendations_by_age(age_group)
        if movies:
            recommendations = movies[:3]
            movie_titles = ", ".join([movie[0] for movie in recommendations])
            ALMemory.raiseEvent("cinema/age_appropriate_movies", movie_titles)
            
    elif value == "show_directions":
        direction_type = ALMemory.getData("cinema/direction_request")
        show_tablet_content("map")
        point_direction(direction_type)
        
    elif value == "concession_recommendations":
        show_concession_menu()
        concession_gesture()
        
    elif value == "take_photo":
        photo_pose()
        ALMemory.raiseEvent("cinema/photo_ready", "true")
        
    elif value == "play_trivia":
        start_trivia_game()
        
    elif value == "emergency_help":
        emergency_gesture()
        ALMemory.raiseEvent("cinema/emergency_alert", "true")
        
    elif value == "calculate_wait_time":
        movie = ALMemory.getData("cinema/selected_movie")
        wait_time = calculate_queue_time(movie)
        ALMemory.raiseEvent("cinema/estimated_wait", str(wait_time))

def show_concession_menu():
    """Display concession menu options"""
    conn = sqlite3.connect(os.path.join(project_path, "data/cinema.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, price FROM concessions ORDER BY category")
    items = cursor.fetchall()
    conn.close()
    
    menu_text = "Our concession menu includes: "
    for item in items[:3]:  # Show top 3 items
        menu_text += "{} for ${:.2f}, ".format(item[0], item[1])
    
    ALMemory.raiseEvent("cinema/concession_menu", menu_text.rstrip(", "))

def calculate_queue_time(movie_title):
    """Calculate estimated wait time based on current queue"""
    # Simple simulation - in real implementation, this would use actual queue data
    base_time = 5  # Base 5 minutes
    popularity_factor = hash(movie_title) % 10  # Simulate popularity
    return base_time + popularity_factor

def start_trivia_game():
    """Start a movie trivia game"""
    trivia_questions = [
        "What movie features a young lion named Simba?",
        "Which movie has the famous line 'May the Force be with you'?",
        "What animated movie features a snowman named Olaf?"
    ]
    
    import random
    question = random.choice(trivia_questions)
    ALMemory.raiseEvent("cinema/trivia_question", question)

def main():
    global project_path, ALMemory, ALDialog, tts_service, ALMotion, tablet_service
    
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ.get('PEPPER_IP', '127.0.0.1'), 
                       help="Robot IP address")
    parser.add_argument("--pport", type=int, required=True, help="Naoqi port number")
    args = parser.parse_args()
    
    # Find project path
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    # Connect to session
    try:
        connection_url = "tcp://{}:{}".format(args.pip, args.pport)
        print("Connecting to {}".format(connection_url))
        app = qi.Application(["Cinema Assistant", "--qi-url=" + connection_url])
    except RuntimeError:
        print("Can't connect to Naoqi at ip {} on port {}.".format(args.pip, args.pport))
        sys.exit(1)
    
    app.start()
    session = app.session
    
    # Initialize database
    initialize_database()
    
    # Create service connections
    ALDialog = session.service('ALDialog')
    ALMemory = session.service('ALMemory')
    ALMotion = session.service("ALMotion")
    tts_service = session.service("ALTextToSpeech")
    
    try:
        tablet_service = session.service("ALTabletService")
    except:
        print("Tablet service not available")
        tablet_service = None
    
    # Setup ALDialog with topic file
    topic_path = os.path.join(project_path, "topicFiles", "main.top")
    topf_path = topic_path.decode('utf-8')
    topic_name = ALDialog.loadTopic(topf_path.encode('utf-8'))
    ALDialog.activateTopic(topic_name)
    ALDialog.subscribe('cinema_assistant')
    
    # Initialize memory variables
    memory_vars = [
        "cinema/customer_name", "cinema/movie_preference", "cinema/selected_movie",
        "cinema/age_group", "cinema/direction_request", "cinema/function",
        "cinema/showtimes", "cinema/concession_order", "cinema/emergency_type",
        "cinema/trivia_answer", "cinema/language_preference"
    ]
    
    for var in memory_vars:
        ALMemory.insertData(var, "")
    
    # Connect function handler
    function_sub = ALMemory.subscriber("cinema/function")
    function_sub.signal.connect(handle_cinema_functions)
    
    print("Cinema Assistant is running... Press Ctrl+C to stop.")
    
    # Main loop
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return graceful_close(ALDialog, topic_name)

if __name__ == "__main__":
    main()