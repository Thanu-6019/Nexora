import numpy as np
from sentence_transformers import SentenceTransformer, util

# Initialize the SentenceTransformer model
# We'll use a small, efficient model for faster processing
model = SentenceTransformer('all-MiniLM-L6-v2')

def match_users_by_skills(user_list: list) -> list:
    """
    Matches users by their skills using cosine similarity on sentence embeddings.
    """
    if len(user_list) < 2:
        return []

    # Combine all user skill strings into a list for embedding
    skill_strings = [user['skills'] for user in user_list]
    
    # Generate embeddings for each user's skills
    skill_embeddings = model.encode(skill_strings, convert_to_tensor=True)

    # Compute cosine similarity between all pairs of embeddings
    cosine_scores = util.cos_sim(skill_embeddings, skill_embeddings)

    matches = []
    # Loop through each user to find their matches
    for i in range(len(user_list)):
        for j in range(i + 1, len(user_list)):
            user1 = user_list[i]
            user2 = user_list[j]
            score = cosine_scores[i][j].item()
            
            # If the similarity score is above a certain threshold, consider it a match
            if score > 0.5:
                matches.append({
                    "user1_id": user1['id'],
                    "user1_name": user1['name'],
                    "user2_id": user2['id'],
                    "user2_name": user2['name'],
                    "similarity_score": round(score, 4)
                })
    return matches

def recommend_events_for_user(user_profile_string: str, event_list: list) -> list:
    """
    Recommends events for a user based on cosine similarity
    between their profile and event tags.
    """
    if not event_list:
        return []

    # Get the embedding for the user's profile string
    user_embedding = model.encode(user_profile_string, convert_to_tensor=True)

    # Get the embeddings for all event tags
    event_tags = [event['tags'] for event in event_list]
    event_embeddings = model.encode(event_tags, convert_to_tensor=True)
    
    # Compute cosine similarity between the user and all events
    cosine_scores = util.cos_sim(user_embedding, event_embeddings)[0]
    
    # Create a list of events with their similarity scores
    scored_events = []
    for i, event in enumerate(event_list):
        scored_events.append({
            "title": event['title'],
            "score": round(cosine_scores[i].item(), 4)
        })

    # Sort events by score in descending order
    scored_events.sort(key=lambda x: x['score'], reverse=True)
    
    # Return the top N recommendations
    return scored_events
