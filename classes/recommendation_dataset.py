import os
import random

class KGBuilder(object):
    def __init__(self, ratings_file="data/ratings.dat",
        users_file="data/users.dat",
        movies_file="data/movies.dat",
        out_train="data/train.txt",
        out_test="data/test.txt",
        out_kg="data/kg.txt",
        test_ratio=0.2, subset_ratio=1.0, subset_method='top_movies'):
        
        self.ratings_file = ratings_file
        self.users_file = users_file
        self.movies_file = movies_file
        self.out_train = out_train
        self.out_test = out_test
        self.out_kg = out_kg
        self.test_ratio = test_ratio
        self.subset_ratio = subset_ratio  # fraction of likes to keep (0.0 to 1.0)
        self.subset_method = subset_method  # 'random', 'top_users', 'top_movies', 'balanced'
        self.user_age_group = {}
        self.movie_genres = {}
        self.likes = []
        self.kg_triples = []
    
    def _map_age_to_group(self, age):
        age = int(age)
        if age == 1:
            return 'child'
        elif age in [18, 25]:
            return 'teen'
        else:
            return 'adult'
    
    def load_users(self):
        with open(self.users_file, 'r') as f:
            for line in f:
                parts = line.strip().split("::")
                if len(parts) < 5:
                    continue
                user_id, gender, age, occ, zip_code = parts
                age_group = self._map_age_to_group(int(age))
                self.user_age_group[user_id] = age_group
                self.kg_triples.append(("user_" + user_id, "has_age", "agegroup_" + age_group))
    
    def load_movies(self):
        with open(self.movies_file, 'r') as f:
            for line in f:
                parts = line.strip().split("::")
                if len(parts) < 3:
                    continue
                movie_id, title, genres = parts
                genre_list = [genre.lower() for genre in genres.split("|")]
                self.movie_genres[movie_id] = genre_list
                for genre in genre_list:
                    self.kg_triples.append(("movie_" + movie_id, "is_genre", "genre_" + genre.replace(" ", "_")))

    def load_ratings(self, min_rating=4):
        with open(self.ratings_file, 'r') as f:
            for line in f:
                parts = line.strip().split("::")
                if len(parts) < 4:
                    continue
                user_id, movie_id, rating, timestamp = parts
                if int(rating) >= min_rating:
                    self.likes.append(("user_" + user_id, "likes", "movie_" + movie_id))
    
    def select_subset(self):
        """Select a subset of likes based on the specified method and ratio"""
        if self.subset_ratio >= 1.0:
            return  # Use all likes
        
        target_size = int(len(self.likes) * self.subset_ratio)
        
        if self.subset_method == 'random':
            # Random sampling
            random.shuffle(self.likes)
            self.likes = self.likes[:target_size]
            
        elif self.subset_method == 'top_users':
            # Keep likes from most active users
            user_counts = {}
            for user, rel, movie in self.likes:
                user_counts[user] = user_counts.get(user, 0) + 1
            
            # Sort users by activity
            sorted_users = sorted(user_counts.keys(), key=lambda u: user_counts[u], reverse=True)
            
            # Select likes from top users until we reach target size
            selected_likes = []
            for user in sorted_users:
                user_likes = [like for like in self.likes if like[0] == user]
                if len(selected_likes) + len(user_likes) <= target_size:
                    selected_likes.extend(user_likes)
                else:
                    # Add remaining likes randomly from this user
                    remaining = target_size - len(selected_likes)
                    random.shuffle(user_likes)
                    selected_likes.extend(user_likes[:remaining])
                    break
            
            self.likes = selected_likes
            
        elif self.subset_method == 'top_movies':
            # Keep likes for most popular movies
            movie_counts = {}
            for user, rel, movie in self.likes:
                movie_counts[movie] = movie_counts.get(movie, 0) + 1
            
            # Sort movies by popularity
            sorted_movies = sorted(movie_counts.keys(), key=lambda m: movie_counts[m], reverse=True)
            
            # Select likes for top movies until we reach target size
            selected_likes = []
            for movie in sorted_movies:
                movie_likes = [like for like in self.likes if like[2] == movie]
                if len(selected_likes) + len(movie_likes) <= target_size:
                    selected_likes.extend(movie_likes)
                else:
                    # Add remaining likes randomly from this movie
                    remaining = target_size - len(selected_likes)
                    random.shuffle(movie_likes)
                    selected_likes.extend(movie_likes[:remaining])
                    break
            
            self.likes = selected_likes
            
        elif self.subset_method == 'balanced':
            # Try to maintain user-movie distribution balance
            user_movie_likes = {}
            for user, rel, movie in self.likes:
                if user not in user_movie_likes:
                    user_movie_likes[user] = []
                user_movie_likes[user].append((user, rel, movie))
            
            # Sample proportionally from each user
            selected_likes = []
            users = list(user_movie_likes.keys())
            
            while len(selected_likes) < target_size and users:
                for user in users[:]:  # Copy list to avoid modification during iteration
                    if user_movie_likes[user]:
                        like = user_movie_likes[user].pop(0)
                        selected_likes.append(like)
                        if len(selected_likes) >= target_size:
                            break
                    else:
                        users.remove(user)
            
            self.likes = selected_likes
        
        print("Selected likes out of original using  method")
    
    def split_likes(self):
        random.shuffle(self.likes)
        test_size = int(len(self.likes) * self.test_ratio)
        test_likes = self.likes[:test_size]
        train_likes = self.likes[test_size:]
        
        with open(self.out_train, 'w') as f_train:
            for triple in train_likes:
                f_train.write("%s\t%s\t%s\n" % triple)
        
        with open(self.out_test, 'w') as f_test:
            for triple in test_likes:
                f_test.write("%s\t%s\t%s\n" % triple)
        
        return train_likes
    
    def save_kg(self, train_likes):
        with open(self.out_kg, 'w') as f:
            for triple in train_likes + self.kg_triples:
                f.write("%s\t%s\t%s\n" % triple)
    
    def build_kg(self):
        self.load_users()
        self.load_movies()
        self.load_ratings()
        self.select_subset()  # Add this line to select subset
        train_likes = self.split_likes()
        self.save_kg(train_likes)
        print("Finished building KG.")

    def load_kg_file(self):
        triples = []
        with open(self.out_kg, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 3:
                    triples.append(tuple(parts))
        return triples


if __name__ == "__main__":
    # Example usage with different subset methods:
    
    # Use 50% of likes randomly
    builder = KGBuilder(
        subset_ratio=0.1,
        subset_method='top_movies'
    )
    builder.build_kg()