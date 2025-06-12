# -*- coding: utf-8 -*-
from datetime import datetime
from .motion_manager import greeting_gesture, emergency_gesture, point_direction


# Queste variabili devono essere passate da fuori
ALMemory = None
db = None
current_customer = None
tablet_service = None

def show_tablet_content(content_type, data=None):
    """Display content on Pepper's tablet"""
    if tablet_service:
        if content_type == "movies":
            tablet_service.showWebview("file:///opt/aldebaran/www/movies.html")
        elif content_type == "showtimes":
            tablet_service.showWebview("file:///opt/aldebaran/www/showtimes.html")
        elif content_type == "map":
            tablet_service.showWebview("file:///opt/aldebaran/www/cinema_map.html")

def set_dependencies(memory, database, tablet):
    """Inietta dipendenze esterne (ALMemory, db)"""
    global ALMemory, db, tablet_service
    ALMemory = memory
    db = database
    tablet_service = tablet

def handle_cinema_functions(value):
    global current_customer
    print("Handling cinema function", value)
    
    if value == "greet_customer":
        greeting_gesture()
        current_customer = {"interaction_start": datetime.now()}
        
    elif value == "check_movie_preference":
        print("Checking movie preference...")
        preference = ALMemory.getData("cinema/movie_preference")
        print("Customer preference:", preference)
        movies = db.get_movies_by_genre(preference)
        print("Movies found:", movies)
        if movies:
            movie_list = ", ".join([movie[0] for movie in movies[:3]])
            ALMemory.raiseEvent("cinema/movie_suggestions", movie_list)
            print("Suggested movies:", movie_list)
        
    elif value == "get_showtimes":
        movie_title = ALMemory.getData("cinema/selected_movie")
        showtimes = db.get_showtimes_for_movie(movie_title)
        if showtimes:
            time_list = ", ".join([showtime[0] for showtime in showtimes])
            ALMemory.raiseEvent("cinema/available_times", time_list)
            show_tablet_content("showtimes", showtimes)
            
    elif value == "show_directions":
        direction_type = ALMemory.getData("cinema/direction_request")
        show_tablet_content("map")
        point_direction(direction_type)
        
    elif value == "emergency_help":
        emergency_gesture()
        ALMemory.raiseEvent("cinema/emergency_alert", "true")
