# -*- coding: utf-8 -*-
# database.py

import json
import os

class Database:
    def __init__(self):
        self.patients = {}
        self.db_file = "patients_db.json"
        self.load_database()

    def load_database(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                try:
                    self.patients = json.load(f)
                    print "Database loaded from %s" % self.db_file
                except ValueError: # Per JSONDecodeError in Python 2.7
                    print "Error decoding JSON from %s. Starting with an empty database." % self.db_file
                    self.patients = {}
        else:
            print "No existing database file found. Starting with an empty database."

    def save_database(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.patients, f, indent=4)
            print "Database saved to %s" % self.db_file

    def addPatient(self, name):
        if name not in self.patients:
            self.patients[name] = {
                "movies": {
                    "preferences": { # Contatore per generi visti/preferiti
                        "action": 0,
                        "comedy": 0,
                        "drama": 0,
                        "sci-fi": 0,
                        "horror": 0,
                        "thriller": 0,
                        "animation": 0,
                        "adventure": 0,
                        "family": 0,
                        "romance": 0,
                        "sport": 0
                    },
                    "watched": [],
                    "liked": [],
                    "disliked": []
                }
            }
            self.save_database()

    def get_available_movies(self):
        return [
            {"title": "Dune Part Two", "genre": ["sci-fi", "action", "adventure"], "year": 2024, "plot": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family."},
            {"title": "Kung Fu Panda 4", "genre": ["animation", "comedy", "action"], "year": 2024, "plot": "Po must train a new Dragon Warrior while a shapeshifting sorceress plans to steal his Staff of Wisdom."},
            {"title": "Godzilla x Kong The New Empire", "genre": ["action", "sci-fi", "thriller"], "year": 2024, "plot": "Godzilla and Kong must unite to fight a colossal undiscovered threat hidden within our world."},
            {"title": "The Fall Guy", "genre": ["action", "comedy"], "year": 2024, "plot": "A stuntman who left the business after an accident must track down a missing film star."},
            {"title": "Challengers", "genre": ["drama", "romance", "sport"], "year": 2024, "plot": "Tashi, a former tennis prodigy, transforms her husband into a Grand Slam champion. To jolt him out of a losing streak, she makes him play a Challenger event where he faces her ex-boyfriend."},
            {"title": "Inside Out 2", "genre": ["animation", "comedy", "family"], "year": 2024, "plot": "Riley's mind is undergoing a complete demolition to make room for new emotions. Joy, Sadness, Anger, Fear, and Disgust aren't sure how to feel when Anxiety shows up."},
            {"title": "IF", "genre": ["comedy", "family", "fantasy"], "year": 2024, "plot": "A young girl gains the ability to see imaginary friends and embarks on a magical adventure."},
            {"title": "Furiosa A Mad Max Saga", "genre": ["action", "sci-fi", "adventure"], "year": 2024, "plot": "The origin story of renegade warrior Furiosa before her encounter with Mad Max."}
        ]

    def update_movie_preference(self, user_name, genre):
        if user_name in self.patients and genre in self.patients[user_name]["movies"]["preferences"]:
            self.patients[user_name]["movies"]["preferences"][genre] += 1
            self.save_database()
            print "Updated %s preference for %s" % (genre, user_name)

    def add_watched_movie(self, user_name, movie_title):
        if user_name in self.patients and movie_title not in self.patients[user_name]["movies"]["watched"]:
            self.patients[user_name]["movies"]["watched"].append(movie_title)
            self.save_database()
            print "%s added to watched list for %s" % (movie_title, user_name)

    def add_liked_movie(self, user_name, movie_title):
        if user_name in self.patients and movie_title not in self.patients[user_name]["movies"]["liked"]:
            self.patients[user_name]["movies"]["liked"].append(movie_title)
            self.save_database()
            print "%s added to liked list for %s" % (movie_title, user_name)

    def add_disliked_movie(self, user_name, movie_title):
        if user_name in self.patients and movie_title not in self.patients[user_name]["movies"]["disliked"]:
            self.patients[user_name]["movies"]["disliked"].append(movie_title)
            self.save_database()
            print "%s added to disliked list for %s" % (movie_title, user_name)