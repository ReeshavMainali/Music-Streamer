from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, CustomUser
from .forms import UserProfileForm
from music.utils import get_mongodb_connection

@login_required
def profile_view(request):
    """Display and edit user profile"""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user.profile)
    
    # Get listening history from MongoDB
    db = get_mongodb_connection()
    history_collection = db['listening_history']
    listening_history = list(history_collection.find(
        {'user_id': str(user.id)},
        {'_id': 0}
    ).sort('timestamp', -1).limit(10))
    
    context = {
        'user': user,
        'form': form,
        'listening_history': listening_history
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def update_genres(request):
    """Update user's favorite genres"""
    if request.method == 'POST':
        genre_ids = request.POST.getlist('genres')
        user = request.user
        user.profile.favorite_genres.clear()
        for genre_id in genre_ids:
            user.profile.favorite_genres.add(genre_id)
        user.profile.save()
        messages.success(request, 'Your favorite genres have been updated!')
        return redirect('profile')
    
    return redirect('profile')