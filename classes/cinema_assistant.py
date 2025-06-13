from datetime import datetime

class CinemaAssistant(object):
    def __init__(self, memory, database, tablet, motion_manager):
        self.memory = memory
        self.db = database
        self.tablet = tablet
        self.motion = motion_manager
    
    def handle_function(self, value):
        print("Handling function:", value)

        if value == "greet_customer":
            self.motion.greeting()
            
            # Reset flags on new greeting
            name = self.memory.getData("cinema/customer_name")
            customer = self.db.get_customer_by_name(name)
            if customer:
                self.memory.raiseEvent("cinema/customer_identity_check", 
                    "True")
                self.current_customer = customer

            else:
                self.memory.raiseEvent("cinema/customer_identity_check", 
                    "False")

        elif value == "register_customer":
            name = self.memory.getData("cinema/customer_name")
            age = self.memory.getData("cinema/customer_age")
            genre=self.memory.getData("cinema/movie_preference")
            if name and age:
                print("Registering customer")
                self.db.register_customer(name, age,genre)
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
            name = self.memory.getData("cinema/customer_name")
            age = self.memory.getData("cinema/customer_age")
            genre = self.memory.getData("cinema/movie_preference")

            # Fetch missing age or genre from DB
            if not age or not genre:
                customer = self.db.get_customer_by_name(name)
                age, genre = customer[1], customer[2]
                print(age, genre)

            # Fetch movies by genre and age group
            movies_by_genre = self.db.get_movies_by_genre(genre)  # Returns list of tuples
            movies_by_age = self.db.get_recommendations_by_age(age)  # Returns list of tuples
            print(movies_by_genre,movies_by_age)
            # Extract titles and use sets for intersection
            titles_genre = set(m[0] for m in movies_by_genre)
            titles_age = set(m[0] for m in movies_by_age)

            # Prioritize movies that match both genre and age
            common_titles = list(titles_genre & titles_age)

            if len(common_titles) < 3:
                # Fill remaining spots with genre-specific titles (if needed)
                remaining = list(titles_genre - set(common_titles))
                suggestions = common_titles + remaining[:3 - len(common_titles)]
            else:
                suggestions = common_titles[:3]

            suggestion_str = ", ".join(suggestions)
            self.memory.raiseEvent("cinema/movie_suggestions",
                "Here are some %s movies you might like: %s." % (genre, suggestion_str))

           

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


        

