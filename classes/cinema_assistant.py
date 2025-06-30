from datetime import datetime
import re

class CinemaAssistant(object):
    def __init__(self, memory, database, mws, motion_manager):
        self.memory = memory
        self.db = database
        self.mws = mws
        self.motion = motion_manager
        self.current_order = []  # Track items for order
    
        action = "goodbye"
        # remove old buttons
        mws.csend("im.executeModality('BUTTONS', [])")
        mws.csend("im.execute('{}')".format(action))
        print("ESEGUITO ACTION ")
        
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
            
            print("Registering customer")
            self.db.register_customer(name, age,genre)
            print("Customer registered successfully.")

        elif value == "update_preferences":
            name = self.memory.getData("cinema/customer_name")
            genre = self.memory.getData("cinema/movie_preference")
            self.db.update_customer_preferences(name, genre)

        elif value == "recommend_movies":
            name = self.memory.getData("cinema/customer_name")
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
                # Fill remaining spots with age-specific titles (if needed)
                #Cosi te ne consiglia 3 al momento perche ora ci sono solo un film per genere
                # mentre per eta ci sono piu film
                remaining = list(titles_age - set(common_titles))
                suggestions = common_titles + remaining[:3 - len(common_titles)]
            else:
                suggestions = common_titles[:3]

            suggestion_str = ", ".join(suggestions)
            self.memory.raiseEvent("cinema/movie_suggestions", suggestion_str)

        elif value == "get_showtimes":
            title = self.memory.getData("cinema/selected_movie")
            try:
                showtimes = self.db.get_showtimes_for_movie(title)

                #Really important to check if showtimes is empty and send exception
                var_used_to_get_exception = showtimes[0][0]  

                times = ", ".join([s[0] for s in showtimes])
                self.memory.raiseEvent("cinema/available_times", times)
            
            except Exception as e:
                print("The film is not in our Cinema:", str(e))
                self.memory.raiseEvent("cinema/showtimes_failed", 
                    "Sorry, the film is not in our cinema")

        #Prende un film (anche uno non tra i consigliati)
        elif value == "get_description":
            title = self.memory.getData("cinema/selected_movie")
            try:
                description = self.db.get_description_for_movie(title)[0][0]
                self.memory.raiseEvent("cinema/description", description)
            
            except Exception as e:
                print("The film is not in our Cinema:", str(e))
                self.memory.raiseEvent("cinema/description_failed", 
                    "Sorry, the film is not in our cinema")
            
            
        elif value == "book_showtime":

            name = self.memory.getData("cinema/customer_name")
            title = self.memory.getData("cinema/selected_movie")
            show_time = self.memory.getData("cinema/selected_time")
            try:
                self.db.book_showtime(name, title, show_time)
                self.memory.raiseEvent("cinema/booking_success", 
                    "Booking confirmed")
            except Exception as e:
                print("Errore nella prenotazione:", str(e))
                self.memory.raiseEvent("cinema/booking_failed", 
                    "Sorry, booking failed: " + str(e))

        if value == "show_directions":
            # Point and give verbal directions without moving
            location = self.memory.getData("cinema/direction_request")
            screen_number = None

            if location:
                # Try to extract screen number from location string
                match = re.search(r"screen\s*([0-9]+)", location.lower())
                print("Location:", location)
                print("Match:", match)
                if match:
                    screen_number = int(match.group(1))
                    location="screen"

                verbal_direction = self.motion.point_and_describe_direction(location, screen_number)
                if verbal_direction == "You're already there!":
                    self.memory.raiseEvent("cinema/already_there", verbal_direction)
                else:
                    self.memory.raiseEvent("cinema/direction_indication", verbal_direction)
        
        elif value == "guide_to_screen":
            screen_number = self.db.get_screen_for_movie(self.memory.getData("cinema/selected_movie"))
            if screen_number:
                # Store screen number in memory for dialog reference
                self.motion.guide_to_location("screen", screen_number)
                self.memory.raiseEvent("cinema/screen_guidance_complete", str(screen_number))
            else:
                print("Screen not found for movie.")
                self.memory.raiseEvent("cinema/screen_guidance_failed", "Screen not found for movie.")
                
        elif value == "guide_to_location":
            # New generalized guidance function
            location = self.memory.getData("cinema/target_location")
            screen_number = None
            
            if location:
                match = re.search(r"screen\s*([0-9]+)", location.lower())
                if match:
                    screen_number = int(match.group(1))
                    location="screen"
                self.motion.guide_to_location(location, screen_number)
                event_message = "Arrived at {}".format(location)
                if screen_number:
                    event_message += " {}".format(screen_number)
                self.memory.raiseEvent("cinema/guidance_complete", event_message)
            else:
                print("No target location specified.")
                self.memory.raiseEvent("cinema/guidance_failed", "No target location specified.")

        elif value == "concession_info":
            self.motion.concession()
            items = self.db.get_concessions()
            names = ", ".join([item[0] for item in items])
            self.memory.raiseEvent("cinema/concession_list", "We have: " + names + ". Would you like to order something?")


        elif value == "list_all_movies":
            print("Listing all available movies:")
        
            movies = self.db.get_all_movies()
            
            movie_list = ", ".join([movie[0] for movie in movies])
            print("Available movies:", movie_list)
            self.memory.raiseEvent("cinema/all_movies_list", movie_list)

        elif value == "add_to_order":
            item = self.memory.getData("cinema/selected_concession")
            item_db = self.db.get_concession_item(item)

            if item_db:
                self.current_order.append((item_db[1],item_db[3]))
                self.memory.raiseEvent("cinema/concession_found", "True")
            else:
                self.memory.raiseEvent("cinema/concession_found", "False")
    
        elif value == "finalize_order":
            if not self.current_order:
                self.memory.raiseEvent("cinema/order_error", "Empty order")
            else:
                complete_order = ", ".join(item[0] for item in self.current_order)
                self.memory.insertData("cinema/complete_order", complete_order)
                total = sum(item[1] for item in self.current_order)  # Assuming price is index 1
                self.memory.insertData("cinema/order_total", total)
                self.memory.raiseEvent("cinema/order_complete", str(total))
                self.current_order = []  # Clear after processing
        
        elif value == "restart":
            for key in self.memory.getDataList("cinema/"):
                self.memory.insertData(key, "")
            self.memory.raiseEvent("cinema/restart", "True")
            
        elif value == "cancel_order":
            self.current_order = []



