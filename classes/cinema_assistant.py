from datetime import datetime

class CinemaAssistant(object):
    def __init__(self, memory, database, tablet, motion_manager):
        self.memory = memory
        self.db = database
        self.tablet = tablet
        self.motion = motion_manager
        self.current_customer = None
        self.name_collected = False
        self.age_collected = False
        self.genre_confirmed = False

    def handle_function(self, value):
        print("Handling function:", value)

        if value == "greet_customer":
            self.motion.greeting()
            self.current_customer = {"interaction_start": datetime.now()}
            # Reset flags on new greeting
            self.name_collected = False
            self.age_collected = False
            self.genre_confirmed = False

        elif value == "register_customer":
            name = self.memory.getData("cinema/customer_name")
            age = self.memory.getData("cinema/customer_age")
            if name and age:
                print("Registering customer")
                self.db.register_customer(name, age)
                self.name_collected = True
                self.age_collected = True
                print("Customer registered successfully.")
            else:
                print("Name or age missing for registration.")

        elif value == "update_preferences":
            name = self.memory.getData("cinema/customer_name")
            genre = self.memory.getData("cinema/movie_preference")
            if name and genre:
                self.db.update_customer_preferences(name, genre)
                self.genre_confirmed = True
            else:
                print("Name or genre missing for updating preferences.")

        elif value == "recommend_movies":
            if not (self.name_collected and self.age_collected):
                # Ask user to provide name and age first
                self.memory.raiseEvent("cinema/request_info", 
                    "Please tell me your name and age group first.")
                return
            if not self.genre_confirmed:
                self.memory.raiseEvent("cinema/request_genre", 
                    "What kind of movies do you like? For example, action, comedy, or sci-fi?")
                return
            self.recommend_movies()

        elif value == "get_showtimes":
            title = self.memory.getData("cinema/selected_movie")
            if not title:
                self.memory.raiseEvent("cinema/request_movie", "Please specify the movie you want showtimes for.")
                return
            showtimes = self.db.get_showtimes_for_movie(title)
            if showtimes:
                times = ", ".join([s[0] for s in showtimes])
                self.memory.raiseEvent("cinema/available_times", times)
                self.tablet.showWebview("file:///opt/aldebaran/www/showtimes.html")
            else:
                self.memory.raiseEvent("cinema/no_showtimes", "Sorry, no showtimes found for %s." % title)

        elif value == "show_directions":
            direction = self.memory.getData("cinema/direction_request")
            if direction:
                self.tablet.showWebview("file:///opt/aldebaran/www/cinema_map.html")
                self.motion.point_direction(direction)
            else:
                self.memory.raiseEvent("cinema/no_direction", "Sorry, I didn't understand where you want to go.")

        elif value == "emergency_help":
            self.motion.emergency()
            self.memory.raiseEvent("cinema/emergency_alert", "true")

        elif value == "concession_info":
            self.motion.concession()
            items = self.db.get_concessions()
            if items:
                names = ", ".join([item[0] for item in items])
                self.memory.raiseEvent("cinema/concession_list", "We have: " + names + ". Would you like to order something?")
            else:
                self.memory.raiseEvent("cinema/no_concessions", "Sorry, we have no concessions right now.")

    def recommend_movies(self):
        name = self.memory.getData("cinema/customer_name")
        age = self.memory.getData("cinema/customer_age")
        genre = self.memory.getData("cinema/movie_preference")

        if genre:
            movies = self.db.get_movies_by_genre(genre)
        else:
            movies = self.db.get_recommendations_by_age(age)

        if movies:
            suggestions = ", ".join([m[0] for m in movies[:3]])
            self.memory.raiseEvent("cinema/movie_suggestions", 
                "Here are some %s movies you might like: %s." % (genre, suggestions))
        else:
            self.memory.raiseEvent("cinema/no_recommendations", "Sorry, no movies found for your preferences.")
