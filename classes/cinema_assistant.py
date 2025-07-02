from datetime import datetime
import re
import io
import os
import time

class CinemaAssistant(object):
    def __init__(self, memory, database, mws, motion_manager):
        self.memory = memory
        self.db = database
        self.mws = mws
        self.motion = motion_manager
        self.current_order = []  # Track items for order

        
    def handle_function(self, value):
        print("Handling function:", value)

        if value == "greet_customer":

            self.motion.greeting()
            # Reset flags on new greeting
            name = self.memory.getData("cinema/customer_name")
            customer = self.db.get_customer_by_name(name)
            if customer:
                self.current_customer = customer

                text = {
                    ("*", "*", "it", "*"): "Bentornato {}".format(name),
                    ("*", "*", "*", "*"): "Welcome back {}".format(name)
                }

                self.create_action(text = text, filename="welcome-back")
                action = "welcome-back"
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('{}')".format(action))
                self.memory.raiseEvent("cinema/customer_identity_check", 
                    "True")
                
            else:
                # Create new customer welcome action
                text = {
                    ("*", "*", "it", "*"): "Benvenuto nel nostro cinema! Raccogliamo alcune informazioni per migliorare la tua esperienza.",
                    ("*", "*", "*", "*"): "Welcome to our cinema! Let's gather some information to enhance your experience."
                }
                
                self.create_action(
                    image="images/new_customer_welcome.jpg",
                    text=text,
                    filename="new-customer-welcome"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('new-customer-welcome')")
                self.memory.raiseEvent("cinema/customer_identity_check", 
                    "False")

        elif value == "register_customer":
            name = self.memory.getData("cinema/customer_name")
            age = self.memory.getData("cinema/customer_age")
            genre=self.memory.getData("cinema/movie_preference")
            
            print("Registering customer")
            self.db.register_customer(name, age,genre)
            print("Customer registered successfully.")
            # Create registration success action
            text = {
                ("*", "*", "it", "*"): "Perfetto {}! Il tuo profilo e stato creato. Preferenza: {} per eta {}.".format(name, genre, age),
                ("*", "*", "*", "*"): "Perfect {}! Your profile has been created. Preference: {} for age group {}.".format(name, genre, age)
            }
            
            self.create_action(
                image="images/registration_success.jpg",
                text=text,
                filename="registration-success"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('registration-success')")


        elif value == "update_preferences":
            name = self.memory.getData("cinema/customer_name")
            genre = self.memory.getData("cinema/movie_preference")
            self.db.update_customer_preferences(name, genre)
            # Create registration success action
            text = {
                ("*", "*", "it", "*"): "Perfetto {}! Il tuo profilo e stato aggiornato. Preferenza: {}.".format(name, genre),
                ("*", "*", "*", "*"): "Perfect {}! Your profile has been updated. Preference: {}.".format(name, genre)
            }
            
            self.create_action(
                image="images/update_success.jpg",
                text=text,
                filename="update-success"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('update-success')")

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
            text = {
                ("*", "*", "it", "*"): "****",
                ("*", "*", "*", "*"): "Some movies you could like are: {}".format(suggestion_str)
            }
            
            self.create_action(
                image="images/recommend_movies.jpg",
                text=text,
                filename="recommend-movies"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('recommend-movies')")

            self.memory.raiseEvent("cinema/movie_suggestions", suggestion_str)

        elif value == "get_showtimes":
            title = self.memory.getData("cinema/selected_movie")
            try:
                showtimes = self.db.get_showtimes_for_movie(title)

                #Really important to check if showtimes is empty and send exception
                var_used_to_get_exception = showtimes[0][0]  

                times = ", ".join([s[0] for s in showtimes])

                # Create showtimes display action
                text = {
                    ("*", "*", "it", "*"): "Orari disponibili per '{}': {}".format(title, times),
                    ("*", "*", "*", "*"): "Available showtimes for '{}': {}".format(title, times)
                }
                
                # # Create buttons for each showtime (Non serve, solo execute)
                # buttons = {}
                # for i, showtime in enumerate(showtimes):
                #     buttons["time_{}".format(i)] = {
                #         "it": showtime[0],
                #         "en": showtime[0]
                #     }
                
                self.create_action(
                    image="images/showtimes.jpg",
                    text=text,
                    filename="showtimes-display"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('showtimes-display')")

                self.memory.raiseEvent("cinema/available_times", times)
                
            
            except Exception as e:
                print("The film is not in our Cinema:", str(e))

                text = {
                    ("*", "*", "it", "*"): "Scusate, il film non e disponibile nel nostro cinema.",
                    ("*", "*", "*", "*"): "Sorry, the film is not available in our cinema."
                }

                self.create_action(
                    image="images/showtimes-error.jpg",
                    text=text,
                    filename="showtimes-error"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('showtimes-error')")

                self.memory.raiseEvent("cinema/showtimes_failed", 
                    "Sorry, the film is not in our cinema")

        #Prende un film (anche uno non tra i consigliati)
        elif value == "get_description":
            title = self.memory.getData("cinema/selected_movie")
            try:
                description = self.db.get_description_for_movie(title)[0][0]

                text = {
                    ("*", "*", "it", "*"): "{}".format(description),
                    ("*", "*", "*", "*"): "{}".format(description)
                }
                
                self.create_action(
                    image="images/movie_poster_{}.jpg".format(title.lower().replace(" ", "_")),
                    text=text,
                    filename="movie-description"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('movie-description')")

                self.memory.raiseEvent("cinema/description", description)
            
            except Exception as e:
                print("The film is not in our Cinema:", str(e))
                
                text = {
                    ("*", "*", "it", "*"): "Scusate, il film non e disponibile nel nostro cinema.",
                    ("*", "*", "*", "*"): "Sorry, the film is not available in our cinema."
                }

                self.create_action(
                    image="images/description-error.jpg",
                    text=text,
                    filename="description-error"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('description-error')")
                self.memory.raiseEvent("cinema/description_failed", 
                    "Sorry, the film is not in our cinema")
            
            
        elif value == "book_showtime":

            name = self.memory.getData("cinema/customer_name")
            title = self.memory.getData("cinema/selected_movie")
            show_time = self.memory.getData("cinema/selected_time")
            try:
                self.db.book_showtime(name, title, show_time)
                text = {
                    ("*", "*", "it", "*"): "Prenotazione confermata!\nFilm: {}\nOrario: {}\nRitira i biglietti alla biglietteria.".format(title, show_time),
                    ("*", "*", "*", "*"): "Booking confirmed!\nMovie: {}\nTime: {}\nCollect your tickets at the box office.".format(title, show_time)
                }
                
                self.create_action(
                    image="images/booking_success.jpg",
                    text=text,
                    filename="booking-success"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('booking-success')")

                self.memory.raiseEvent("cinema/booking_success", 
                    "Booking confirmed")
            except Exception as e:
                print("Errore nella prenotazione:", str(e))

                text = {
                    ("*", "*", "it", "*"): "Prenotazione fallita. Riprova.",
                    ("*", "*", "*", "*"): "Booking failed. Retry."
                }
                self.create_action(
                    image="images/booking_error.jpg",
                    text=text,
                    filename="booking-error"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('booking-error')")

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

                text = {
                    ("*", "*", "it", "*"): "Direzioni per {}".format(location),
                    ("*", "*", "*", "*"): "Directions to {}" .format(location)
                }
                
                self.create_action(
                    image="img/cinema_map_path.png",  # The generated map
                    text=text,
                    filename="directions-with-map"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('directions-with-map')")
            

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

            text = {
                ("*", "*", "it", "*"): "Abbiamo: {}. Vuoi ordinare qualcosa?".format(names),
                ("*", "*", "*", "*"): "We have: {}. Would you like to order something?".format(names)
            }
            self.create_action(
                image="images/concessions.jpg",
                text=text,
                filename="concession-list"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('concession-list')")

            self.memory.raiseEvent("cinema/concession_list", "We have: " + names + ". Would you like to order something?")


        elif value == "list_all_movies":
            print("Listing all available movies:")
        
            movies = self.db.get_all_movies()
            
            movie_list = ", ".join([movie[0] for movie in movies])
            print("Available movies:", movie_list)

            # Create all movies display action
            text = {
                ("*", "*", "it", "*"): "Film attualmente in programmazione: {}".format(movie_list),
                ("*", "*", "*", "*"): "Movies currently showing: {}".format(movie_list)
            }
            
            # Create buttons for each movie
            # buttons = {}
            # for i, movie in enumerate(movies[:8]):  # Limit to 8 movies for display
            #     buttons["movie_{}".format(i)] = {
            #         "it": movie[0],
            #         "en": movie[0]
            #     }
            
            self.create_action(
                image="images/all_movies.jpg",
                text=text,
                filename="all-movies-display"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('all-movies-display')")

            self.memory.raiseEvent("cinema/all_movies_list", movie_list)

        elif value == "add_to_order":
            item = self.memory.getData("cinema/selected_concession")
            item_db = self.db.get_concession_item(item)

            if item_db:
                self.current_order.append((item_db[1],item_db[3]))

                text = {
                    ("*", "*", "it", "*"): "{} aggiunto al tuo ordine.".format(item_db[1]),
                    ("*", "*", "*", "*"): "{} added to your order.".format(item_db[1])
                }
                self.create_action(
                    image="images/order_success.jpg",
                    text=text,
                    filename="order-success"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('order-success')")

                self.memory.raiseEvent("cinema/concession_found", "True")
            else:

                text = {
                    ("*", "*", "it", "*"): "Scusate, l'articolo non e disponibile.",
                    ("*", "*", "*", "*"): "Sorry, the item is not available."
                }
                self.create_action(
                    image="images/concession_error.jpg",
                    text=text,
                    filename="concession-error"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('concession-error')")

                self.memory.raiseEvent("cinema/concession_found", "False")
    
        elif value == "finalize_order":
            if not self.current_order:
                text = {
                    ("*", "*", "it", "*"): "Il tuo ordine e vuoto.",
                    ("*", "*", "*", "*"): "Your order is empty."
                }
                self.create_action(
                    image="images/order_empty.jpg",
                    text=text,
                    filename="order-empty"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('order-empty')")
                self.memory.raiseEvent("cinema/order_error", "Empty order")
            else:
                complete_order = ", ".join(item[0] for item in self.current_order)
                self.memory.insertData("cinema/complete_order", complete_order)
                total = sum(item[1] for item in self.current_order)  # Assuming price is index 1
                self.memory.insertData("cinema/order_total", total)
                text = {
                    ("*", "*", "it", "*"): "Il tuo ordine e completo: {}. Totale: {} euro.".format(complete_order, total),
                    ("*", "*", "*", "*"): "Your order is complete: {}. Total: {} euros.".format(complete_order, total)
                }
                self.create_action(
                    image="images/order_complete.jpg",  
                    text=text,
                    filename="order-complete"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('order-complete')")

                self.memory.raiseEvent("cinema/order_complete", str(total))
                self.current_order = []  # Clear after processing
        
        elif value == "restart":
            for key in self.memory.getDataList("cinema/"):
                self.memory.insertData(key, "")
            self.motion.guide_to_location("entrance")
            text = {
                ("*", "*", "it", "*"): "Addio.",
                ("*", "*", "*", "*"): "Goodbye."
            }
            self.create_action(
                image="images/goodbye.jpg",
                text=text,
                filename="goodbye"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('goodbye')")
            self.memory.raiseEvent("cinema/restart", "True")
            
            
        elif value == "cancel_order":
            text = {
                ("*", "*", "it", "*"): "Il tuo ordine e stato cancellato.",
                ("*", "*", "*", "*"): "Your order has been cancelled."
            }
            self.create_action(
                image="images/order_cancelled.jpg",
                text=text,
                filename="order-cancelled"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('order-cancelled')")
            self.current_order = []



    def handle_tablet(self, value):
        print("Handling tablet:", value)
        if value == "tablet_main_hub":
            text = {
                ("*", "*", "it", "*"): "Siamo nel main hub.",
                ("*", "*", "*", "*"): "We are in main hub."
            }

            self.create_action(
                image="img/cinema.png",
                text=text,
                filename="main-hub"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('main-hub')")


    def create_action(self, image=None, text=None, tts=None, buttons=None, filename="actions"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        actions_dir = os.path.join(base_dir, "tablet", "actions")
        if not os.path.exists(actions_dir):
            os.makedirs(actions_dir)

        full_path = os.path.join(actions_dir, filename)

        with open(full_path, "w") as f:
            # IMAGE Section
            if image:
                f.write(u"IMAGE\n<*, *, *, *>:  {}\n----\n".format(unicode(image)))

            # TEXT Section
            if text:
                f.write(u"TEXT\n")
                for key, value in text.items():
                    key_str = u", ".join([unicode(k) for k in key])
                    f.write(u"<{}>: {}\n".format(key_str, unicode(value)))
                f.write(u"----\n")

            # TTS Section
            if tts:
                f.write(u"TTS\n")
                for key, value in tts.items():
                    key_str = u", ".join([unicode(k) for k in key])
                    f.write(u"<{}>: {}\n".format(key_str, unicode(value)))
                f.write(u"----\n")

            # BUTTONS Section
            if buttons:
                f.write(u"BUTTONS\n")
                for btn_key, translations in buttons.items():
                    it_text = translations.get("it", "")
                    en_text = translations.get("en", "")
                    f.write(u"{}\n".format(unicode(btn_key)))
                    f.write(u"<*,*,it,*>: {}\n".format(unicode(it_text)))
                    f.write(u"<*,*,*,*>:  {}\n".format(unicode(en_text)))
                f.write(u"----\n")

