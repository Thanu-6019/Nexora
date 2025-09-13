from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Dict

# This is a pre-trained model that converts sentences into vectors.
# The 'all-MiniLM-L6-v2' model is a great balance of size and performance.
model = SentenceTransformer('all-MiniLM-L6-v2')

def match_users_by_skills(users: List[Dict], max_matches_per_user: int = 3) -> Dict:
    """
    Matches users based on the semantic similarity of their skills and interests.
    It returns a dictionary where each user is mapped to a list of their top matches.
    
    Args:
        users (List[Dict]): A list of user dictionaries, where each dict contains 'id', 'name', and 'skills'.
                            Example: [{'id': 1, 'name': 'Alice', 'skills': 'Python, Machine Learning'}, ...]
        max_matches_per_user (int): The maximum number of matches to return for each user.

    Returns:
        Dict: A dictionary of user matches.
              Example: {'Alice': [{'name': 'Bob', 'similarity': 0.85}, {'name': 'Charlie', 'similarity': 0.72}]}
    """
    if not users or len(users) < 2:
        print("Not enough users for matching.")
        return {}

    # Extract all skills and names from the user data
    user_skills = [user['skills'] for user in users]
    user_names = [user['name'] for user in users]

    # Convert the skill strings into numerical vectors (embeddings)
    print("Generating embeddings for all users...")
    embeddings = model.encode(user_skills, convert_to_tensor=True)

    # Calculate the cosine similarity between all user embeddings
    cosine_scores = util.cos_sim(embeddings, embeddings)

    matches = {}
    for i in range(len(users)):
        # Get the scores for the current user against all other users
        scores = cosine_scores[i]
        # Find the indices of the top matches, excluding the user themselves
        top_indices = np.argsort(scores.cpu().numpy())[::-1][1:max_matches_per_user + 1]
        
        user_matches = []
        for index in top_indices:
            user_matches.append({
                'name': user_names[index],
                'similarity': scores[index].item()
            })
        matches[user_names[i]] = user_matches
        
    return matches

def recommend_events_for_user(user_profile: str, events: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Recommends events for a single user based on the semantic similarity of their profile
    (skills/interests) to the event tags.

    Args:
        user_profile (str): A string representing the user's skills and interests.
                            Example: 'I am interested in data science, AI, and natural language processing.'
        events (List[Dict]): A list of event dictionaries, where each dict has 'title' and 'tags'.
                             Example: [{'title': 'Data Science Workshop', 'tags': 'data science, python, visualization'}, ...]
        top_n (int): The number of top recommended events to return.

    Returns:
        List[Dict]: A list of recommended events, sorted by similarity score.
                    Example: [{'title': 'Data Science Workshop', 'similarity': 0.92}, ...]
    """
    if not user_profile or not events:
        print("User profile or events list is empty.")
        return []

    # Get the user's profile embedding
    print("Generating user profile embedding...")
    user_embedding = model.encode(user_profile, convert_to_tensor=True)

    # Get the embeddings for all event tags
    event_tags = [event['tags'] for event in events]
    print("Generating embeddings for all event tags...")
    event_embeddings = model.encode(event_tags, convert_to_tensor=True)
    
    # Calculate the similarity between the user and all events
    cosine_scores = util.cos_sim(user_embedding, event_embeddings)[0]
    
    # Pair event titles with their similarity scores and sort
    event_with_scores = []
    for i, score in enumerate(cosine_scores):
        event_with_scores.append({
            'title': events[i]['title'],
            'similarity': score.item()
        })
        
    event_with_scores.sort(key=lambda x: x['similarity'], reverse=True)
    
    return event_with_scores[:top_n]

if __name__ == '__main__':
    # --- Example Usage for User Matching ---
    print("--- User Matching Example ---")
    sample_users = [
        {'id': 1, 'name': 'Alice', 'skills': 'Python, machine learning, deep learning'},
        {'id': 2, 'name': 'Bob', 'skills': 'Data analysis, statistics, R, visualization'},
        {'id': 3, 'name': 'Charlie', 'skills': 'Artificial intelligence, computer vision, neural networks'},
        {'id': 4, 'name': 'Diana', 'skills': 'Web development, Flask, SQL, databases'},
        {'id': 5, 'name': 'Frank', 'skills': 'Python, data science, machine learning, pandas'},
    ]
    
    user_matches = match_users_by_skills(sample_users)
    for user, matches in user_matches.items():
        print(f"\nTop matches for {user}:")
        for match in matches:
            print(f"- {match['name']} (Similarity: {match['similarity']:.2f})")
    
    print("\n" + "-"*30 + "\n")

    # --- Example Usage for Event Recommendation ---
    print("--- Event Recommendation Example ---")
    sample_events = [
        {'title': 'Introduction to Python', 'tags': 'python, beginner, programming'},
        {'title': 'Deep Learning for Beginners', 'tags': 'deep learning, neural networks, machine learning'},
        {'title': 'Web Security Fundamentals', 'tags': 'cybersecurity, web development, security'},
        {'title': 'Advanced Data Science Workshop', 'tags': 'data science, machine learning, statistics, python'},
        {'title': 'Frontend Frameworks in 2024', 'tags': 'web development, javascript, react, vue'},
    ]
    
    user_profile_string = "My interests are in artificial intelligence, machine learning, and programming."
    
    recommended_events = recommend_events_for_user(user_profile_string, sample_events)
    print(f"Top 3 event recommendations for user: '{user_profile_string}'")
    for event in recommended_events:
        print(f"- {event['title']} (Similarity: {event['similarity']:.2f})")

