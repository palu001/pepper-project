from datetime import datetime,timedelta
import random
import re
import io
import os
import time
import ast
from datetime import datetime, timedelta

class CinemaAssistant(object):
    def __init__(self, animation,memory, database, mws, motion_manager):
        self.animation=animation
        self.memory = memory
        self.db = database
        self.mws = mws
        self.motion = motion_manager
        self.current_order = []  # Track items for order
        self.is_tablet=False
        #hour = random.randint(15, 20)
        hour=18
        minute = random.randint(0, 59)
        self.current_time = datetime.strptime("{:02}:{:02}".format(hour, minute), "%H:%M")

        
    def handle_function(self, value):
        print("Handling function:", value)
        if value == "greet_customer":
            self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/Hey_1",_async=True)
            # Reset flags on new greeting
            name = self.memory.getData("cinema/customer_name")
            customer = self.db.get_customer_by_name(name)
            if customer:
                self.current_customer = customer

                text = {
                    ("*", "*", "it", "*"): "Bentornato {}  ".format(name),
                    ("*", "*", "*", "*"): "Welcome back to our cinema {}! ".format(name)
                }
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.create_action(text = text, filename="welcome-back")
                action = "welcome-back"
    
                self.mws.csend("im.execute('{}')".format(action))
                self.memory.raiseEvent("cinema/customer_identity_check", 
                    "True")
                
            else:
                self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/Enthusiastic_4",_async=True)
                # Create new customer welcome action
                text = {
                    ("*", "*", "it", "*"): "Benvenuto nel nostro cinema! Raccogliamo alcune informazioni per migliorare la tua esperienza.",
                    ("*", "*", "*", "*"): "Welcome to our cinema! Let's gather some information to enhance your experience."
                }
                
                self.create_action(
                    image="img/cinema.png",
                    text=text,
                    filename="new-customer-welcome"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('new-customer-welcome')")
                self.memory.raiseEvent("cinema/customer_identity_check", 
                    "False")
     
        elif value == "check_upcoming_showtime":
            name = self.memory.getData("cinema/customer_name")
            booking = self.db.get_unrated_movie_for_customer(name)
            if not booking:
                self.memory.raiseEvent("cinema/upcoming_showtime", "False")
            else:
                title, show_time_str, screen_number = booking
                show_time = datetime.strptime(show_time_str, "%H:%M")

                print(show_time,self.current_time)
                time_diff = (show_time - self.current_time).total_seconds() / 60
                print(time_diff)
                if 0 <= time_diff <= 15:
                    self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/Excited_1",_async=True)
                    self.memory.insertData("cinema/upcoming_movie_title", title)
                    self.memory.insertData("cinema/upcoming_showtime_time", show_time.strftime("%-I:%M %p"))
                    self.memory.insertData("cinema/screen_number", str(screen_number))
                    self.memory.raiseEvent("cinema/upcoming_showtime", "True")
                else:
                    self.memory.raiseEvent("cinema/upcoming_showtime", "False")
            
          
                
        elif value == "check_for_feedback":
            name = self.memory.getData("cinema/customer_name")
            booking = self.db.get_unrated_movie_for_customer(name)
            
            if booking:
                unrated_movie, show_time_str, screen_number = booking
                show_time = datetime.strptime(show_time_str, "%H:%M")
                print("cur,show",self.current_time,show_time)
                if self.current_time>show_time:
                    self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/Thinking_4",_async=True)
                    self.memory.insertData("cinema/last_watched_movie", unrated_movie)
                    self.memory.raiseEvent("cinema/feedback_needed", "True")
                else:
                    self.memory.raiseEvent("cinema/feedback_needed", "False")
            else:
                self.memory.raiseEvent("cinema/feedback_needed", "False")
        
        elif value == "main_hub":
                self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/BodyTalk/BodyTalk_10",_async=True)
                text = {
                    ("*", "*", "it", "*"): "Come posso aiutarti?",
                    ("*", "*", "*", "*"): "How can I help you?"
                }
                buttons = {
                    "tablet_concessions": {
                        "it": "Concessioni",
                        "en": "Concessions"
                    },
                    "tablet_recommendations": {
                        "it": "Consigli",
                        "en": "Recommendations"
                    },
                    "tablet_showtimes": {
                        "it": "Orari",
                        "en": "Showtimes"
                    },
                    "tablet_directions": {
                        "it": "Indicazioni",
                        "en": "Directions"
                    },
                    'tablet_genre': {
                        'it': "Modifica Genere",
                        'en': "Update Genre"
                    },
                    'tablet_restart':{
                        'it':"Riavvia",
                        'en':"Restart"
                    }
                }
                self.create_action(
                    image="img/cinema.png",
                    text=text,
                    filename="main-hub",
                    buttons=buttons
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('main-hub')")
    
        elif value == "register_customer":
            name = self.memory.getData("cinema/customer_name")
            age = self.memory.getData("cinema/customer_age")
            genre=self.memory.getData("cinema/movie_preference")
            
            print("Registering customer")
            self.db.register_customer(name, age,genre)
            print("Customer registered successfully.")
            self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/Yes_1",_async=True)
            # Create registration success action
            text = {
                ("*", "*", "it", "*"): "Perfetto {}! Il tuo profilo e stato creato.  Would you like to use tablet in order to communicate?".format(name),
                ("*", "*", "*", "*"): "Perfect {}! Your profile has been created.  Would you like to use tablet in order to communicate?".format(name)
            }
            
            self.create_action(
                image="img/registration_success.jpeg",
                text=text,
                filename="registration-success"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('registration-success')")


        elif value == "record_feedback":
            name = self.memory.getData("cinema/customer_name")
            movie = self.memory.getData("cinema/last_watched_movie")
            liked = self.memory.getData("cinema/liked_status") # True or False

            self.db.record_movie_feedback(name, movie, liked)

            # Get user and movie details to form a smart reply.
            user_profile = self.db.get_customer_by_name(name)
            user_genre = user_profile[2] if user_profile else "any"
            movie_details = self.db.get_movie_details(movie) # Assumes DB returns a dict with a 'genre' key
            movie_genre = movie_details['genre'] if movie_details else "unknown"

            response_text = ""
            if liked == 'True':
                self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Emotions/Positive/Happy_4",_async=True)
                if movie_genre.lower() == user_genre.lower():
                    response_text = "I'm so glad you liked it! It sounds like the perfect {} movie for you.".format(movie_genre)
                else:
                    response_text = "That's great! It's always fun to discover a gem outside of your usual {} preference.".format(user_genre)
            else:  # Disliked
                self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Emotions/Neutral/Embarrassed_1",_async=True)
                if movie_genre.lower() == user_genre.lower():
                    response_text = "Oh, that's a shame. Even though it's a {} film, this one wasn't for you. I'll remember that for future recommendations.".format(movie_genre)
                else:
                    response_text = "I see. That's understandable, since it's a bit different from the {} films you usually prefer. Thanks for the feedback!".format(user_genre)

            
            if not self.is_tablet:
                self.memory.raiseEvent("cinema/feedback_response", response_text)
            else:
                self.memory.insertData("cinema/feedback_response",response_text)



        elif value == "update_preferences":
            name = self.memory.getData("cinema/customer_name")
            genre = self.memory.getData("cinema/movie_preference")
            self.db.update_customer_preferences(name, genre)
            # Create registration success action
            self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/Yes_2",_async=True)
            text = {
                ("*", "*", "it", "*"): "Perfetto {}! Il tuo profilo e stato aggiornato. Preferenza: {}.".format(name, genre),
                ("*", "*", "*", "*"): "Perfect {}! Your profile has been updated. Preference: {}.".format(name, genre)
            }
            
            self.create_action(
                image="img/booking_success.png",
                text=text,
                filename="update-success"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('update-success')")

        elif value == "recommend_movies":
            self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/YouKnowWhat_1",_async=True)
            name = self.memory.getData("cinema/customer_name")
            customer = self.db.get_customer_by_name(name)
            customer_id,name,age, genre = customer
            liked_count = self.db.get_liked_movie_count(customer_id)
            print(age, genre,liked_count)

            available_movies = self.db.get_available_showtime_titles()
            available_titles_set = set(available_movies)

            if liked_count > 1:
                # Recommend using RotatE model
                recommendations = self.db.load_model_and_recommend(name)  # This returns a list of movie names (strings)
                # Intersect with available showtimes
                suggestions = [title for title in recommendations if title in available_titles_set][:3]
            else:
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
                ("*", "*", "*", "*"): "Some movies you could like are: "
            }

            buttons = {}
            for i, movie in enumerate(suggestions):
                buttons["movie_{}".format(i)] = {
                    "it": movie,
                    "en": movie
                }
            
            self.create_action(
                image="img/recommend_movies.jpeg",
                text=text,
                filename="recommend-movies",
                buttons=buttons
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('recommend-movies')")
            self.memory.raiseEvent("cinema/movie_suggestions", suggestion_str)
            
        #Da modificare per ask
        elif value == "get_showtimes":

            title = self.memory.getData("cinema/selected_movie")
            title=re.sub(r'\(\s+(\d{4})\s*\)', r'(\1)', title)
            try:
                showtimes = self.db.get_showtimes_for_movie(title)
                print("showww",showtimes)

                #Really important to check if showtimes is empty and send exception
                var_used_to_get_exception = showtimes[0][0]  

                times = ", ".join([s[0] for s in showtimes])
                times_split=[s.strip() for s in times.split(',')]

                

                # Create showtimes display action
                text = {
                    ("*", "*", "it", "*"): "Orari disponibili per '{}': ".format(title),
                    ("*", "*", "*", "*"): "Available showtimes for '{}': ".format(title)
                }
                
                # Create buttons for each showtime (Non serve, solo execute)
                buttons = {}
                for i, showtime in enumerate(times_split):
                    buttons["time_{}".format(i)] = {
                        "it": showtime,
                        "en": showtime
                    }
                
                self.create_action(
                    image="img/movie_poster_{}.jpeg".format(title.lower().replace(" ", "_")),
                    text=text,
                    buttons=buttons,
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
                    image="img/showtimes-error.jpeg",
                    text=text,
                    filename="showtimes-error"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('showtimes-error')")

                self.memory.raiseEvent("cinema/showtimes_failed", 
                    "Sorry, the film is not in our cinema")

        #Prende un film (anche uno non tra i consigliati)
        elif value == "get_description":
            self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/YouKnowWhat_2",_async=True)
            title = self.memory.getData("cinema/selected_movie")
            title=re.sub(r'\(\s+(\d{4})\s*\)', r'(\1)', title)
            try:
                print("descrizioneegafaf",self.db.get_description_for_movie(title))
                description = self.db.get_description_for_movie(title)[0][0]

                text = {
                    ("*", "*", "it", "*"): "{}".format(description),
                    ("*", "*", "*", "*"): "{}".format(description)
                }

                self.create_action(
                    image="img/movie_poster_{}.jpeg".format(title.lower().replace(" ", "_")),
                    text=text,
                    filename="movie-description",
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
                    image="img/booking_error.jpeg",
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
            title=re.sub(r'\(\s+(\d{4})\s*\)', r'(\1)', title)
            show_time = self.memory.getData("cinema/selected_time")
            try:
                self.db.book_showtime(name, title, show_time)
                text = {
                    ("*", "*", "it", "*"): "Prenotazione confermata!\nFilm: {}\nOrario: {}\nRitira i biglietti alla biglietteria.".format(title, show_time),
                    ("*", "*", "*", "*"): "Booking confirmed!\nMovie: {}\nTime: {}\nCollect your tickets at the box office.".format(title, show_time)
                }
                
                self.create_action(
                    image="img/booking_success.png",
                    text=text,
                    filename="booking-success"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('booking-success')")
                self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Emotions/Positive/Hysterical_1",_async=True)
                self.memory.raiseEvent("cinema/booking_success", 
                    "Booking confirmed")
            except Exception as e:
                print("Errore nella prenotazione:", str(e))

                text = {
                    ("*", "*", "it", "*"): "Prenotazione fallita. Riprova.",
                    ("*", "*", "*", "*"): "Booking failed. Retry."
                }
                self.create_action(
                    image="img/booking_error.jpeg",
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
            if location == "box office":
                location = "box_office"
            if location == "concession stand":
                location = "concession"
            screen_number = None
            image = "img/{}_path.png".format(location)  # The generated map
            print("image path ", image)
            if location:
                # Try to extract screen number from location string
                match = re.search(r"screen\s*([0-9]+)", location.lower())
                print("Location:", location)
                print("Match:", match)
                if match:
                    screen_number = int(match.group(1))
                    location="screen"
                    image = "img/screen{}_path.png".format(screen_number)  # Specific screen path

                verbal_direction = self.motion.point_and_describe_direction(location, screen_number)

                text = {
                    ("*", "*", "it", "*"): "Direzioni per {}".format(location),
                    ("*", "*", "*", "*"): "Directions to {}" .format(location)
                }
                self.create_action(
                    image=image,  # The generated map
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
            title=self.memory.getData("cinema/selected_movie")
            title=re.sub(r'\(\s+(\d{4})\s*\)', r'(\1)', title)
            screen_number = self.db.get_screen_for_movie(title)
            if screen_number:
                # Store screen number in memory for dialog reference
                verbal_direction = self.motion.point_and_describe_direction("screen", screen_number)

                text = {
                    ("*", "*", "it", "*"): "Sto guidandoti verso lo schermo {}.".format(screen_number),
                    ("*", "*", "*", "*"): "I am guiding you to screen {}.".format(screen_number)
                }
                self.create_action(
                    image="img/screen{}_path.png".format(screen_number),  # The generated map
                    text=text,
                    filename="screen-guidance"
                )  
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('screen-guidance')")
                self.motion.guide_to_location("screen", screen_number)
                self.memory.raiseEvent("cinema/screen_guidance_complete", str(screen_number))
            else:
                print("Screen not found for movie.")
                self.memory.raiseEvent("cinema/screen_guidance_failed", "Screen not found for movie.")
                
        elif value == "guide_to_location":
            # New generalized guidance function
            location = self.memory.getData("cinema/target_location")
            screen_number = None
            if location == "box office":
                location = "box_office"
            if location == "concession stand":
                location = "concession"
            
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

        elif value == "has_preferred":
             # Ottieni nome utente da memoria
            customer_name = self.memory.getData("cinema/customer_name")
            print("customer name: ",customer_name)
            # Ottieni cibo preferito (piuordinato)
            preferred_item = self.db.get_most_ordered_concession(customer_name)           
            print("pref item name: ",preferred_item)
            if preferred_item:
                self.memory.insertData("cinema/preferred_item", preferred_item[0])
                print("calling true")
                self.memory.raiseEvent("cinema/preferred_list", "True")

            else:
                print("calling false")
                self.memory.raiseEvent("cinema/preferred_list", "False")
             
        elif value == "preferred_buy":
            preferred_item = self.memory.getData("cinema/preferred_item")

            text = {
                ("*", "*", "it", "*"): "Vuoi ordinare qualcosa? Abbiamo: " + preferred_item ,
                ("*", "*", "*", "*"): "Hey, welcome back to the bar! I know you really like " + preferred_item +" would you like to add it to cart?"
            }

            buttons = {}
            buttons["yes"] = {
                "it": "yes",
                "en": "yes"
            }
            buttons["no"] = {
                "it": "no",
                "en": "no"
            }

            self.create_action(
                image="img/concessions.jpeg",
                text=text,
                buttons=buttons,
                filename="preferred-list"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('preferred-list')")
            self.memory.raiseEvent("cinema/preferred_buy", "True")

        elif value == "concession_info":
            #self.motion.concession()
            self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/ShowTablet_2",_async=True)
            items = self.db.get_concessions()
            names = ", ".join([item[0] for item in items])
            concessions_split = [s.strip() for s in names.split(',')]

            # Ottieni nome utente da memoria
            customer_name = self.memory.getData("cinema/customer_name")

            # Ottieni cibo preferito (piuordinato)

            text = {
                ("*", "*", "it", "*"): "Vuoi ordinare qualcosa? Abbiamo: " + names + ".",
                ("*", "*", "*", "*"): "Would you like to order something? We have: " + names + "." 
            }

            buttons = {}
            for i, concession in enumerate(concessions_split):
                buttons["concession_{}".format(i)] = {
                    "it": concession,
                    "en": concession
                }

            self.create_action(
                image="img/concessions.jpeg",
                text=text,
                buttons=buttons,
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
            movie_split=[s.strip() for s in movie_list.split(',')]
        
            print("movie_split",movie_split)

            # Create all movies display action
            text = {
                ("*", "*", "it", "*"): "Film attualmente in programmazione: ",
                ("*", "*", "*", "*"): "Movies currently showing: "
            }
            
            buttons = {}
            for i, movie in enumerate(movie_split):
                buttons["movie_{}".format(i)] = {
                    "it": movie,
                    "en": movie
                }
            self.create_action(
                image="img/all_movies.jpeg",
                text=text,
                buttons=buttons,
                filename="all-movies-display"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('all-movies-display')")
            self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/ShowTablet_3",_async=True)
            self.memory.raiseEvent("cinema/all_movies_list", movie_list)

        elif value == "add_to_order":
            item = self.memory.getData("cinema/selected_concession")
            item_db = self.db.get_concession_item(item)

            if item_db:
                self.current_order.append((item_db[1],item_db[3]))
            
                text = {
                    ("*", "*", "it", "*"): "{} aggiunto al tuo ordine. Qualcos'altro?".format(item_db[1]),
                    ("*", "*", "*", "*"): "{} added to your order. Anything else?".format(item_db[1])
                }

                self.create_action(
                    image="img/order_success.png",
                    text=text,
                    filename="concession-repeat"
                )
                
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('concession-repeat')")
                self.memory.raiseEvent("cinema/concession_found", "True")
            else:
                text = {
                    ("*", "*", "it", "*"): "Scusate, l'articolo non e disponibile.",
                    ("*", "*", "*", "*"): "Sorry, the item is not available."
                }
                self.create_action(
                    image="img/concession_error.jpeg",
                    text=text,
                    filename="concession-error"
                )

                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('concession-error')")
                self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Emotions/Positive/Happy_4",_async=True)
                self.memory.raiseEvent("cinema/concession_found", "False")
    
        elif value == "finalize_order":
            if not self.current_order:
                text = {
                    ("*", "*", "it", "*"): "Il tuo ordine e vuoto.",
                    ("*", "*", "*", "*"): "Your order is empty."
                }
                self.create_action(
                    image="img/booking_error.jpeg",
                    text=text,
                    filename="order-empty"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('order-empty')")
                self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/Desperate_1",_async=True)
                self.memory.raiseEvent("cinema/order_error", "Empty order")
            else:
                complete_order = ", ".join(item[0] for item in self.current_order)
                self.memory.insertData("cinema/complete_order", complete_order)
                total = sum(item[1] for item in self.current_order)
                self.memory.insertData("cinema/order_total", total)

                # --- AGGIORNAMENTO DELLA TABELLA DEGLI ORDINI ---
                from collections import Counter
                item_names = [item[0] for item in self.current_order]
                counts = Counter(item_names)

                expanded_list = []
                for name, count in counts.items():
                    expanded_list.extend([name] * count)

                customer_name = self.memory.getData("cinema/customer_name")
                self.db.place_concession_order_list(customer_name, expanded_list)

                # Pulisci ordine corrente
                
                text = {
                    ("*", "*", "it", "*"): "Il tuo ordine e completo: {}. Totale: {} euro.".format(complete_order, total),
                    ("*", "*", "*", "*"): "Your order is complete: {}. Total: {} euros.".format(complete_order, total)
                }

                self.create_action(
                    image="img/order_complete.jpg",
                    text=text,
                    filename="order-complete"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('order-complete')")
                self.current_order = []

                self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/Excited_1",_async=True)
                self.memory.raiseEvent("cinema/order_complete", str(total))

        elif value == "restart":
            self.animation.run(".lastUploadedChoregrapheBehavior/animations/Stand/Gestures/Hey_1",_async=True)
            for key in self.memory.getDataList("cinema/"):
                self.memory.insertData(key, "")
            text = {
                ("*", "*", "it", "*"): "Addio.",
                ("*", "*", "*", "*"): "Goodbye."
            }
            self.create_action(
                image="img/cinema.png",
                text=text,
                filename="goodbye"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('goodbye')")
            self.motion.guide_to_location("entrance")
            self.memory.raiseEvent("cinema/restart", "True")
            
            
        elif value == "cancel_order":
            text = {
                ("*", "*", "it", "*"): "Il tuo ordine e stato cancellato.",
                ("*", "*", "*", "*"): "Your order has been cancelled."
            }
            self.create_action(
                image="img/booking_error.jpeg",
                text=text,
                filename="order-cancelled"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('order-cancelled')")
            self.current_order = []


    def handle_tablet(self, value):
        print("Handling tablet event:", value)

        if value == "tablet_main_hub":
            
            text = {
                ("*", "*", "it", "*"): "Come posso aiutarti?",
                ("*", "*", "*", "*"): "How can I help you?"
            }
            buttons = {
                "tablet_concessions": {
                    "it": "Concessioni",
                    "en": "Concessions"
                },
                "tablet_recommendations": {
                    "it": "Consigli",
                    "en": "Recommendations"
                },
                "tablet_showtimes": {
                    "it": "Orari",
                    "en": "Showtimes"
                },
                "tablet_directions": {
                    "it": "Indicazioni",
                    "en": "Directions"
                },
                'tablet_genre': {
                    'it': "Modifica Genere",
                    'en': "Update Genre"
                },
                'tablet_restart':{
                    'it':"Riavvia",
                    'en':"Restart"
                }
            }
            self.create_action(
                image="img/cinema.png",
                text=text,
                filename="main-hub",
                buttons=buttons
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            answer = self.mws.csend("im.ask('main-hub', timeout=999)")
            self.memory.raiseEvent("cinema/tablet_main_hub", answer)

        
        elif value == "tablet_list_all_movies":
            print("Listing all available movies:")
        
            movies = self.db.get_all_movies()
            
            movie_list = ", ".join([movie[0] for movie in movies])
            print("Available movies:", movie_list)
            movie_split=[s.strip() for s in movie_list.split(',')]
        
            print("movie_split",movie_split)

            # Create all movies display action
            text = {
                ("*", "*", "it", "*"): "Film attualmente in programmazione: ",
                ("*", "*", "*", "*"): "Movies currently showing: "
            }
            
            buttons = {}
            for i, movie in enumerate(movie_split):
                buttons["movie_{}".format(i)] = {
                    "it": movie,
                    "en": movie
                }
            buttons["cancel"] = {
                "it" : "cancella",
                "en" : "cancel"
            }
            self.create_action(
                image="img/all_movies.jpeg",
                text=text,
                buttons=buttons,
                filename="all-movies-display"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            answer = self.mws.csend("im.ask('all-movies-display', timeout = 999)")
            self.memory.raiseEvent("tablet/all_movies_list", movie_list)
            if answer == "cancel":
                self.memory.raiseEvent("tablet/cancel_choice", "True")
            else:
                print("Film selected:", buttons[answer]["en"])
                self.memory.insertData("cinema/selected_movie", buttons[answer]["en"])
                self.memory.raiseEvent("tablet/movie_selected", "True")

        elif value == "tablet_get_showtimes":

            title = self.memory.getData("cinema/selected_movie")
            
            showtimes = self.db.get_showtimes_for_movie(title)

            times = ", ".join([s[0] for s in showtimes])
            times_split=[s.strip() for s in times.split(',')]

            

            # Create showtimes display action
            text = {
                ("*", "*", "it", "*"): "Orari disponibili per '{}': ".format(title),
                ("*", "*", "*", "*"): "Available showtimes for '{}': ".format(title)
            }
            
            # Create buttons for each showtime (Non serve, solo execute)
            buttons = {}
            for i, showtime in enumerate(times_split):
                buttons["time_{}".format(i)] = {
                    "it": showtime,
                    "en": showtime
                }
            
            self.create_action(
                image="img/movie_poster_{}.jpeg".format(title.lower().replace(" ", "_")),
                text=text,
                buttons=buttons,
                filename="showtimes-display"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            answer = self.mws.csend("im.ask('showtimes-display', timeout = 999)")

            print("Time selected:", buttons[answer]["en"])
            self.memory.insertData("cinema/selected_time", buttons[answer]["en"])
            self.memory.raiseEvent("tablet/choose_time", "True")
    
        elif value == "tablet_book_showtime":
            name = self.memory.getData("cinema/customer_name")
            title = self.memory.getData("cinema/selected_movie")
            show_time = self.memory.getData("cinema/selected_time")
            print("prima del db")
            self.db.book_showtime(name, title, show_time)
            print("booked")
            text = {
                ("*", "*", "it", "*"): "Prenotazione confermata!\nFilm: {}\nOrario: {}\nRitira i biglietti alla biglietteria.".format(title, show_time),
                ("*", "*", "*", "*"): "Booking confirmed!\nMovie: {}\nTime: {}\nCollect your tickets at the box office.".format(title, show_time)
            }
            
            self.create_action(
                image="img/booking_success.png",
                text=text,
                filename="booking-success"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('booking-success')")

            self.memory.raiseEvent("tablet/booking_success", "True")


             
        elif value == "tablet_genre":
            name = self.memory.getData("cinema/customer_name")
            genres = ["action", "comedy", "drama", "horror", "romance", "sci-fi", "science fiction", "thriller", "documentary", "animated", "family", "adventure", "fantasy"]
            text = {
                ("*", "*", "it", "*"): "Quale genere preferisci, {}?".format(name),
                ("*", "*", "*", "*"): "What genre do you prefer, {}?".format(name)
            }
            buttons = {}
            for i, genre in enumerate(genres):
                print("Genre button:", genre)
                buttons["genre_{}".format(i)] = {
                    "it": genre.capitalize(),
                    "en": genre.capitalize()
                }
            
            self.create_action(
                image="img/cinema.png",
                text=text,
                filename="genre-selection",
                buttons=buttons
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            answer = self.mws.csend("im.ask('genre-selection', timeout=999)")
            print("Genre selected:", answer)
            if answer.startswith("genre_"):
                genre_index = int(answer.split("_")[1])
                genre = genres[genre_index]
                self.db.update_customer_preferences(name, genre)
                text = {
                    ("*", "*", "it", "*"): "Perfetto {}! Il tuo profilo e stato aggiornato. Preferenza: {}.".format(name, genre),
                    ("*", "*", "*", "*"): "Perfect {}! Your profile has been updated. Preference: {}.".format(name, genre)
                }
                
                self.create_action(
                    image="img/booking_success.png",
                    text=text,
                    filename="update-success"
                )
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('update-success')")
                self.memory.raiseEvent("cinema/tablet_genre_selected", "True")

        elif value == "tablet_concessions":
            self.motion.concession()
            items = self.db.get_concessions()
            names = ", ".join([item[0] for item in items])
            concessions_split=[s.strip() for s in names.split(',')]
            self.memory.insertData("cinema/tablet_concession_list", "We have: " + names + ". Would you like to order something?")
            
            text = {
                ("*", "*", "it", "*"): "Vuoi ordinare qualcosa? Abbiamo: ",
                ("*", "*", "*", "*"): "Would you like to order something? We have: " 
            }
            buttons={}
            for i, concession in enumerate(concessions_split):
                    buttons["concession_{}".format(i)] = {
                        "it": concession,
                        "en": concession
                    }
            buttons["cancel"] = {
                "it" : "cancella", 
                "en" : "cancel"
            }

            self.create_action(
                image="img/concessions.jpeg",
                text=text,
                buttons=buttons,
                filename="concession-list"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            answer= self.mws.csend("im.ask('concession-list', timeout=999)")
            if answer == "cancel":
                self.memory.raiseEvent("cinema/tablet_cancel","True")
            else:
                cibo = buttons[answer]["en"]
                print("CIBO: ",cibo)

                self.memory.insertData("cinema/selected_concession", cibo)
                self.memory.raiseEvent("cinema/tablet_add",cibo)

        elif value == "tablet_add_to_order":
            item = self.memory.getData("cinema/selected_concession")
            item_db = self.db.get_concession_item(item)
            self.current_order.append((item_db[1],item_db[3]))
        
            text = {
                ("*", "*", "it", "*"): "{} aggiunto al tuo ordine. Qualcos'altro?".format(item_db[1]),
                ("*", "*", "*", "*"): "{} added to your order. Anything else?".format(item_db[1])
            }
            buttons = {}
            buttons["yes"] = {
                "it" : "si", 
                "en" : "yes"
            }
            buttons["done"] = {
                "it" : "done", 
                "en" : "done"
            }

            self.create_action(
                image="img/order_success.png",
                text=text,
                buttons = buttons,
                filename="concession-repeat"
            )
            
            self.mws.csend("im.executeModality('BUTTONS', [])")
            answer = self.mws.csend("im.ask('concession-repeat', timeout=999)")
            if answer == "yes":
                self.memory.raiseEvent("cinema/tablet_repeat","True")
            else:
                self.memory.raiseEvent("cinema/tablet_repeat","False")


        elif value == "tablet_cancel_order":
            text = {
                ("*", "*", "it", "*"): "Il tuo ordine e stato cancellato.",
                ("*", "*", "*", "*"): "Your order has been cancelled."
            }
            self.create_action(
                image="img/booking_error.jpeg",
                text=text,
                filename="order-cancelled"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('order-cancelled')")
            self.current_order = []

        elif value == "tablet_finalize_order":

            complete_order = ", ".join(item[0] for item in self.current_order)
            self.memory.insertData("cinema/complete_order", complete_order)
            total = sum(item[1] for item in self.current_order)  # Assuming price is index 1
            self.memory.insertData("cinema/order_total", total)
            text = {
                ("*", "*", "it", "*"): "Il tuo ordine e completo: {}. Totale: {} euro.".format(complete_order, total),
                ("*", "*", "*", "*"): "Your order is complete: {}. Total: {} euros.".format(complete_order, total)
            }
            buttons = {}
            self.create_action(
                image="img/order_complete.jpg",  
                text=text,
                buttons = buttons,
                filename="order-complete"
            )

            self.memory.raiseEvent("cinema/tablet_order_complete", str(total))
            self.current_order = []  # Clear after processing

            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('order-complete')")
        
        elif value == "tablet_choose_directions":
            # Ask for directions to a specific location
            text = {
                ("*", "*", "it", "*"): "Dove vuoi andare?",
                ("*", "*", "*", "*"): "Where do you want to go?"
            }
            directions = ["bathroom", "screen 1", "screen 2", "screen 3", "screen 4", "screen 5", "screen 6" ,"screen 7", "screen 8", "concession stand", "exit", "entrance", "box office"]
            buttons = {}
            for i, direction in enumerate(directions):
                buttons["direction_{}".format(i)] = {
                    "it": direction,
                    "en": direction
                }
            self.create_action(
                image="img/cinema.png",
                text=text,
                filename="direction-selection",
                buttons=buttons
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            answer = self.mws.csend("im.ask('direction-selection', timeout=999)")
            print("Direction selected:", buttons[answer]["en"])
            self.memory.insertData("cinema/direction_request", buttons[answer]["en"])
            self.memory.raiseEvent("cinema/tablet_directions_chosen", "True")

        elif value == "tablet_guide_to_location":
            # New generalized guidance function
            location = self.memory.getData("cinema/direction_request")
            if location == "box office":
                location = "box_office"
            if location == "concession stand":
                location = "concession"
            screen_number = None

            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('directions-with-map')")

            if location:
                match = re.search(r"screen\s*([0-9]+)", location.lower())
                if match:
                    screen_number = int(match.group(1))
                    location="screen"
                self.motion.guide_to_location(location, screen_number)
                event_message = "Arrived at {}".format(location)
                if screen_number:
                    event_message += " {}".format(screen_number)
                self.memory.raiseEvent("cinema/tablet_guidance_complete", event_message)
        
        elif value == "tablet_confirm_guide_to_location":
            text = {
                ("*", "*", "it", "*"): "Ti accompagno alla tua destionazione?",
                ("*", "*", "*", "*"): "Shall I guide you to your destination?"
            }
            buttons = {
                "yes": {
                    "it": "si",
                    "en": "yes"
                },
                "no": {
                    "it": "no",
                    "en": "no"
                }
            }
            self.create_action(
                image="img/cinema.png",
                text=text,
                filename="guide-to-location",
                buttons=buttons
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            answer = self.mws.csend("im.ask('guide-to-location', timeout=999)")
            print("Guide to location answer:", answer)
            if answer == "yes":
                self.memory.raiseEvent("cinema/tablet_guide_to_location", "True")
            else:
                self.memory.raiseEvent("cinema/tablet_guide_to_location", "False") 


        elif value == "tablet_show_directions":
            # Point and give verbal directions without moving
            location = self.memory.getData("cinema/direction_request")
            if location == "box office":
                location = "box_office"
            if location == "concession stand":
                location = "concession"
            screen_number = None
            image = "img/{}_path.png".format(location)  # The generated map
            print("image path ", image)
            if location:
                # Try to extract screen number from location string
                match = re.search(r"screen\s*([0-9]+)", location.lower())
                print("Location:", location)
                print("Match:", match)
                if match:
                    screen_number = int(match.group(1))
                    location="screen"
                    image = "img/screen{}_path.png".format(screen_number)  # Specific screen path

                verbal_direction = self.motion.point_and_describe_direction(location, screen_number)

                text = {
                    ("*", "*", "it", "*"): "Direzioni per {}".format(location),
                    ("*", "*", "*", "*"): "Directions to {}" .format(location)
                }
                self.create_action(
                    image=image,  # The generated map
                    text=text,
                    filename="directions-with-map"
                )

                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.execute('directions-with-map')")
            
                if verbal_direction == "You're already there!":
                    self.memory.raiseEvent("cinema/tablet_already_there", verbal_direction)
                else:
                    self.memory.raiseEvent("cinema/tablet_direction_indication", verbal_direction)

        elif value == "tablet_show_directions_concession":
            # Point and give verbal directions without moving
            location = self.memory.getData("cinema/direction_request")
            if location == "box office":
                location = "box_office"
            if location == "concession stand":
                location = "concession"
            print("location da trovare: ", location)
            screen_number = None
            image = "img/{}_path.png".format(location)  # The generated map
            print("image path ", image)

            verbal_direction = self.motion.point_and_describe_direction(location, screen_number)

            text = {
                ("*", "*", "it", "*"): "Direzioni per {}".format(location),
                ("*", "*", "*", "*"): "Directions to {}" .format(location)
            }
            buttons = {}
            buttons["done"] = {
                "en": "done",
                "it": "done"
            }
            self.create_action(
                image=image,  # The generated map
                text=text,
                buttons = buttons,
                filename="directions-with-map"
            )

            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.ask('directions-with-map', timeout=999 )")
            print("verbal_direction ", verbal_direction)
            self.memory.raiseEvent("cinema/tablet_directions_done", "True")

        elif value == "tablet_show_directions_box":
            # Point and give verbal directions without moving
            location = self.memory.getData("cinema/direction_request")
            if location == "box office":
                location = "box_office"
            if location == "concession stand":
                location = "concession"
            print("location da trovare: ", location)
            screen_number = None
            image = "img/{}_path.png".format(location)  # The generated map
            print("image path ", image)

            verbal_direction = self.motion.point_and_describe_direction(location, screen_number)

            text = {
                ("*", "*", "it", "*"): "Direzioni per {}".format(location),
                ("*", "*", "*", "*"): "You can retrieve your ticket at the box" .format(location)
            }
            buttons = {}
            buttons["done"] = {
                "en": "done",
                "it": "done"
            }
            self.create_action(
                image=image,  # The generated map
                text=text,
                buttons = buttons,
                filename="directions-with-map"
            )

            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.ask('directions-with-map', timeout=999 )")
            
            self.memory.raiseEvent("cinema/tablet_directions_done", "True")
        
        elif value == "tablet_offer_screen_guidance":
            screen_number = self.db.get_screen_for_movie(self.memory.getData("cinema/selected_movie"))
            if screen_number:
                # Store screen number in memory for dialog reference
                verbal_direction = self.motion.point_and_describe_direction("screen", screen_number)

            
            text = {
                ("*", "*", "it", "*"): "Ti guido al film nella sala {}?".format(screen_number),
                ("*", "*", "*", "*"): "Would you like me to guide you at screen {}".format(screen_number)
            }
            buttons = {}
            buttons["yes"] = {
                "it" : "si", 
                "en" : "yes"
            }
            buttons["no"] = {
                "it" : "no", 
                "en" : "no"
            }
            self.create_action(
                    image="img/screen{}_path.png".format(screen_number),  # The generated map
                    text=text,
                    buttons = buttons,
                    filename="screen-guidance-offer"
                )  
            self.mws.csend("im.executeModality('BUTTONS', [])")
            answer = self.mws.csend("im.ask('screen-guidance-offer', timeout= 999)")
            if answer == "yes":
                self.memory.raiseEvent("tablet/screen_guidance","True")
            else:
                self.memory.raiseEvent("tablet/screen_guidance","False")

   




        elif value == "tablet_guide_to_screen":
            screen_number = self.db.get_screen_for_movie(self.memory.getData("cinema/selected_movie"))
            if screen_number:
                # Store screen number in memory for dialog reference
                verbal_direction = self.motion.point_and_describe_direction("screen", screen_number)

                text = {
                    ("*", "*", "it", "*"): "Sto guidandoti verso lo schermo {}.".format(screen_number),
                    ("*", "*", "*", "*"): "I am guiding you to screen {}.".format(screen_number)
                }
                self.create_action(
                    image="img/screen{}_path.png".format(screen_number),  # The generated map
                    text=text,
                    filename="screen-guidance"
                )  
                self.mws.csend("im.executeModality('BUTTONS', [])")
                self.mws.csend("im.ask('screen-guidance')")
                self.motion.guide_to_location("screen", screen_number)
                self.memory.raiseEvent("cinema/screen_guidance_complete", str(screen_number))
   


        elif value == "tablet_offer_recommendation":

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
                ("*", "*", "*", "*"): "I ran your taste through my brainy algorithm, these movies could be your thing today, hurry up and buy the tickets!"
            }

            buttons = {}
            for i, movie in enumerate(suggestions):
                buttons["movie_{}".format(i)] = {
                    "it": movie,
                    "en": movie
                }
            
            self.create_action(
                image="img/recommend_movies.jpeg",
                text=text,
                filename="recommend-movies",
                buttons=buttons
            )

            self.mws.csend("im.executeModality('BUTTONS', [])")
            answer = self.mws.csend("im.ask('recommend-movies', timeout = 999)")
            choice = buttons[answer]["en"]
            print("recommended movie selceted: ",choice)
            self.memory.insertData("cinema/selected_movie", choice)
            self.memory.raiseEvent("tablet/movie_suggestions", "True")

        elif value == "tablet_get_description":
        
            title = self.memory.getData("cinema/selected_movie")
           
            description = self.db.get_description_for_movie(title)[0][0]

            text = {
                ("*", "*", "it", "*"): "{}".format(description),
                ("*", "*", "*", "*"): "{}".format(description)
            }
            buttons = {}
            buttons["interested"] = {
                "it" : "interested",
                "en" : "interested"
            }
            buttons["cancel"] = {
                "it" : "cancella",
                "en" : "cancel"
            }
            self.create_action(
                image="img/movie_poster_{}.jpeg".format(title.lower().replace(" ", "_")),
                text=text,
                buttons=buttons,
                filename="movie-description",
            )
            
            self.mws.csend("im.executeModality('BUTTONS', [])")
            answer = self.mws.csend("im.ask('movie-description', timeout = 999)")
            self.memory.raiseEvent("cinema/description", description)
            if answer == "cancel":
                self.memory.raiseEvent("tablet/recommend_cancel", "True")
            else: 
                self.memory.raiseEvent("tablet/recommend_choice", "True")




        elif value == "tablet_restart":
            for key in self.memory.getDataList("cinema/"):
                self.memory.insertData(key, "")

            text = {
                ("*", "*", "it", "*"): "Addio.",
                ("*", "*", "*", "*"): "Goodbye."
            }
            self.create_action(
                image="img/cinema.png",
                text=text,
                filename="goodbye"
            )
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('goodbye')")
            self.motion.guide_to_location("entrance")
            self.memory.raiseEvent("cinema/tablet_restart", "True")
    
        elif value == "check_feedback_tablet":
            self.is_tablet=True
            # This block corresponds to the main part of the %get_movie_feedback_tablet proposal
            last_movie = self.memory.getData("cinema/last_watched_movie")
            
            text = {
                ("it", "*", "*", "*"): "Ho visto che hai prenotato un biglietto per {}. Ti e piaciuto?".format(last_movie),
                ("*", "*", "*", "*"): "I see you booked a ticket for {} last time. Did you enjoy it?".format(last_movie)
            }
            buttons = {
                "yes": {
                    "it": "Si",
                    "en": "Yes"
                },
                "no": {
                    "it": "No",
                    "en": "No"
                }
            }

            self.create_action(
                image="img/movie_feedback.png",
                text=text,
                buttons=buttons,
                filename="movie-feedback-request"
            )
            
            # Clear buttons and ask the user for feedback
            self.mws.csend("im.executeModality('BUTTONS', [])")
            answer = self.mws.csend("im.ask('movie-feedback-request', timeout=999)")

            # The user's choice raises an event, corresponding to e:tablet/feedback_movie
            if answer == "yes":
                self.memory.raiseEvent("tablet/feedback_movie", "True")
            elif answer == "no":
                self.memory.raiseEvent("tablet/feedback_movie", "False")

        elif value == "tablet_feedback_response":
            # This block handles the response after the user has given feedback.
            # It corresponds to the u2 sections in the proposal.
            last_movie = self.memory.getData("cinema/last_watched_movie")
            liked = self.memory.getData("cinema/liked_status")
            response=self.memory.getData("cinema/feedback_response")

            if liked:
                response_text = response+ " Since you liked {}".format(last_movie)
                response_text_it = "Visto che ti e piaciuto {}".format(last_movie)
            else:
                response_text = response + " Since you didn't like {}".format(last_movie)
                response_text_it = "Dato che non ti e piaciuto{}.".format(last_movie)
            
            text = {
                ("it", "*", "*", "*"): response_text_it,
                ("*", "*", "*", "*"): response_text
            }

            self.create_action(
                image="img/recommend_movies.jpeg",
                text=text,
                filename="feedback-thank-you"
            )
            
            # Display the confirmation message, then trigger recommendations
            self.mws.csend("im.executeModality('BUTTONS', [])")
            self.mws.csend("im.execute('feedback-thank-you')")
            
            self.memory.raiseEvent("tablet/feedback_response","True")


 

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

