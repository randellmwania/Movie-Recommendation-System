import numpy as np
import pickle
import streamlit as st
import pandas as pd
from surprise import Reader, Dataset, SVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


# Collaborative Filtering
def collaborative_filtering(user_id, movie_id):
    reader = Reader()
    data = Dataset.load_from_df(ratings_data[['userId', 'movieId', 'rating']], reader)
    trainset = data.build_full_trainset()
    
    svd = SVD()
    svd.fit(trainset)
    
    prediction = svd.predict(user_id, movie_id)
    return prediction.est

# Content-Based Filtering
def content_based_filtering(movie, K):
    tfidf = TfidfVectorizer(max_features=200)
    X = tfidf.fit_transform(movies_data['string'])
    
    idx = movie2idx[movie]
    if type(idx) == pd.Series:
        idx = idx.iloc[0]

    movie_index = X[idx]
    scores = cosine_similarity(movie_index, X)
    scores = scores.flatten()
    
    recommended_idx = (-scores).argsort()[1:K+1]
    
    return movies_data['title'].iloc[recommended_idx]

# Hybrid Recommendation System
def hybrid_recommendation(user_id, input_title_or_genre, K=5, collaborative_weight=0.5):
    if input_title_or_genre in movies_data['title'].values:
        movie_id = movie2idx[input_title_or_genre]
        collaborative_score = collaborative_filtering(user_id, movie_id)
        content_based_movies = content_based_filtering(input_title_or_genre, K)
    elif input_title_or_genre in movies_data['genres'].str.split('|').sum():
        # If input is a genre
        content_based_movies = content_based_filtering(input_title_or_genre, K)
        collaborative_score = 0  # No collaborative filtering for genres
    else:
        print("Invalid input. Please enter a valid movie title or genre.")
        return

    # Combine scores
    hybrid_scores = (collaborative_weight * collaborative_score) + ((1 - collaborative_weight) * content_based_movies.index)
    
    # Get the top K movies based on hybrid scores
    top_hybrid_movies = movies_data['title'].iloc[hybrid_scores.argsort()[::-1][:K]]
    
    return top_hybrid_movies



# Load the pickled functions and data
with open('hybrid_recommendation_model.pkl', 'rb') as file:
    loaded_model_data = pickle.load(file)

# Extract the necessary data from the loaded model
ratings_data = loaded_model_data['ratings_data']
movies_data = loaded_model_data['movies_data']
movie2idx = loaded_model_data['movie2idx']
hybrid_recommendation_function = loaded_model_data['hybrid_recommendation']

# Use the loaded function
user_id = 1

# Input field for the user to enter a movie title or genre
user_input = st.text_input("Enter a movie title or genre:")

# Button to trigger the recommendation
if st.button("Get Recommendations"):
    recommended_movies = hybrid_recommendation_function(user_id, user_input)

    # Display the top 5 Hybrid Recommendations
    st.write("Top 5 Hybrid Recommendations:")
    st.write(recommended_movies)