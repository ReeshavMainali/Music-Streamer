from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.conf import settings  # Import settings if needed
from .models import Track
from users.models import Genre
from .forms import TrackUploadForm
from .utils import get_mongodb_connection, record_listening_history, update_listening_status, get_user_recommendations
from .db_storage import MusicFile, CoverImage
import json
import mimetypes

def home(request):
    """Home page view"""
    recent_tracks = Track.objects.all().order_by('-upload_date')[:8]
    genres = Genre.objects.all()
    
    context = {
        'recent_tracks': recent_tracks,
        'genres': genres,
    }
    return render(request, 'music/home.html', context)

@login_required
def dashboard(request):
    """User dashboard with personalized music recommendations"""
    user = request.user
    
    # Get tracks from database
    recent_tracks = Track.objects.all().order_by('-upload_date')[:12]
    
    # Get user's favorite genres
    favorite_genres = user.profile.favorite_genres.all()
    
    # Get tracks matching user's favorite genres
    recommended_tracks = Track.objects.filter(genre__in=favorite_genres).order_by('?')[:8]
    
    # Get MongoDB data for additional recommendations based on listening history
    db = get_mongodb_connection()
    tracks_collection = db['tracks']
    
    # Get recently played tracks from MongoDB
    history_collection = db['listening_history']
    recent_history = list(history_collection.find(
        {'user_id': str(user.id)},
        {'track_id': 1, '_id': 0}
    ).sort('timestamp', -1).limit(10))
    
    recent_track_ids = [h['track_id'] for h in recent_history]
    
    # Get history-based recommendations from MongoDB utility
    mongo_recommendations = get_user_recommendations(user.id)
    
    context = {
        'user': user,
        'recent_tracks': recent_tracks,
        'recommended_tracks': recommended_tracks,
        'favorite_genres': favorite_genres,
        'mongo_recommendations': mongo_recommendations,
    }
    
    return render(request, 'music/dashboard.html', context)

@login_required
def track_detail(request, track_id):
    """Display track details and player"""
    track = get_object_or_404(Track, id=track_id)

    # Convert duration into minutes and seconds
    duration = track.duration or 0
    minutes = duration // 60
    seconds = duration % 60

    # Record listening start in MongoDB
    track_info = {
        'title': track.title,
        'artist': track.artist,
        'genre': str(track.genre.id) if track.genre else None,
    }
    history_id = record_listening_history(request.user.id, track.id, track_info)

    # Get similar tracks
    similar_tracks = Track.objects.filter(genre=track.genre).exclude(id=track.id)[:4]

    context = {
        'track': track,
        'minutes': minutes,
        'seconds': seconds,
        'similar_tracks': similar_tracks,
        'history_id': str(history_id),
    }

    return render(request, 'music/track_detail.html', context)


@login_required
def upload_track(request):
    """Upload a new track"""
    if request.method == 'POST':
        form = TrackUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create track without files first to get an ID
            track = form.save(commit=False)
            track.uploaded_by = request.user
            track.audio_file = ''  # Temporary placeholder
            track.save()
            
            # Now save the files using the track ID
            audio_file = request.FILES['audio_file']
            track.save_audio_file(audio_file)
            
            if 'cover_image' in request.FILES:
                cover_image = request.FILES['cover_image']
                track.save_cover_image(cover_image)
            
            # Save track metadata to MongoDB
            db = get_mongodb_connection()
            tracks_collection = db['tracks']
            
            track_data = {
                'id': str(track.id),
                'title': track.title,
                'artist': track.artist,
                'genre': str(track.genre.id) if track.genre else None,
                'uploader': str(track.uploaded_by.id),
                'upload_date': track.upload_date.isoformat(),
                'duration': track.duration or 0,
                'url': track.audio_url,
                'cover_url': track.cover_url,
            }
            
            tracks_collection.insert_one(track_data)
            
            messages.success(request, 'Your track was uploaded successfully!')
            return redirect('dashboard')
    else:
        form = TrackUploadForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'music/upload_track.html', context)

def track_list(request):
    """List all tracks with filtering options"""
    tracks = Track.objects.all()
    genres = Genre.objects.all()
    
    # Filter by genre if specified
    genre_id = request.GET.get('genre')
    if genre_id:
        tracks = tracks.filter(genre__id=genre_id)
    
    # Search by title or artist
    query = request.GET.get('q')
    if query:
        tracks = tracks.filter(title__icontains=query) | tracks.filter(artist__icontains=query)
    
    context = {
        'tracks': tracks,
        'genres': genres,
        'selected_genre': genre_id,
        'query': query,
    }
    
    return render(request, 'music/track_list.html', context)

@login_required
def update_listen_status(request):
    """AJAX endpoint to update track listening status"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        history_id = data.get('history_id')
        completed = data.get('completed', False)
        
        if history_id:
            update_listening_status(history_id, completed)
            
            # If user completed listening, update their genre preferences
            if completed:
                db = get_mongodb_connection()
                history_collection = db['listening_history']
                history_entry = history_collection.find_one({'_id': history_id})
                
                if history_entry and 'track_info' in history_entry:
                    genre_id = history_entry['track_info'].get('genre')
                    if genre_id:
                        # Add this genre to user's favorites if not already there
                        user = request.user
                        genre = Genre.objects.get(id=genre_id)
                        if genre not in user.profile.favorite_genres.all():
                            user.profile.favorite_genres.add(genre)
            
            return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

def serve_music_file(request, filename):
    """Serve music files from the database"""
    try:
        file_obj = MusicFile.objects.get(name=filename)
        content_type = file_obj.content_type or 'audio/mpeg'
        response = HttpResponse(file_obj.data, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    except MusicFile.DoesNotExist:
        return HttpResponse(status=404)

def serve_cover_image(request, filename):
    """Serve cover images from the database"""
    try:
        file_obj = CoverImage.objects.get(name=filename)
        content_type = file_obj.content_type or 'image/jpeg'
        response = HttpResponse(file_obj.data, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    except CoverImage.DoesNotExist:
        return HttpResponse(status=404)