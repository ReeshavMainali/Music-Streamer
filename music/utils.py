from django.conf import settings
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

def get_mongodb_connection():
    """Get connection to MongoDB database"""
    client = MongoClient(settings.MONGODB_URI)
    return client[settings.MONGODB_NAME]

def record_listening_history(user_id, track_id, track_info):
    """Record user listening history in MongoDB"""
    db = get_mongodb_connection()
    history_collection = db['listening_history']
    
    history_entry = {
        'user_id': str(user_id),
        'track_id': str(track_id),
        'track_info': track_info,
        'timestamp': datetime.datetime.now(),
        'listened_completely': False
    }
    
    history_collection.insert_one(history_entry)
    return history_entry['_id']

def update_listening_status(history_id, listened_completely=True):
    """Update whether a track was listened to completely"""
    db = get_mongodb_connection()
    history_collection = db['listening_history']
    
    history_collection.update_one(
        {'_id': ObjectId(history_id)},
        {'$set': {'listened_completely': listened_completely}}
    )

def get_user_recommendations(user_id):
    """Get personalized music recommendations for user"""
    db = get_mongodb_connection()
    tracks_collection = db['tracks']
    
    # Get user's favorite genres from the tracks they've listened to completely
    history_collection = db['listening_history']
    listened_history = history_collection.find({
        'user_id': str(user_id),
        'listened_completely': True
    })
    
    # Extract track IDs from history
    listened_track_ids = [history['track_id'] for history in listened_history]
    
    # Get genre information for these tracks
    listened_genres = {}
    for track_id in listened_track_ids:
        track = tracks_collection.find_one({'id': track_id})
        if track and 'genre' in track:
            genre_id = track['genre']
            listened_genres[genre_id] = listened_genres.get(genre_id, 0) + 1
    
    # Sort genres by listen count
    sorted_genres = sorted(listened_genres.items(), key=lambda x: x[1], reverse=True)
    top_genres = [genre_id for genre_id, _ in sorted_genres[:3]]
    
    # Get recommendations from top genres
    recommended_tracks = []
    for genre_id in top_genres:
        genre_tracks = list(tracks_collection.find({
            'genre': genre_id,
            'id': {'$nin': listened_track_ids}
        }).limit(5))
        recommended_tracks.extend(genre_tracks)
    
    return recommended_tracks