from django.db import models
from django.conf import settings  # Import settings
from django.utils import timezone
from .db_storage import DatabaseStorage, MusicFile, CoverImage

# Create music and cover storage instances
music_storage = DatabaseStorage(model=MusicFile)
cover_storage = DatabaseStorage(model=CoverImage)

class Track(models.Model):
    """Music track model"""
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    album = models.CharField(max_length=200, blank=True, null=True)
    genre = models.ForeignKey('users.Genre', on_delete=models.SET_NULL, null=True)
    duration = models.IntegerField(blank=True, null=True)  # Duration in seconds
    
    # Use FileField/ImageField with our custom storage
    audio_file = models.FileField(upload_to='tracks/', storage=music_storage)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True, storage=cover_storage)
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.title} - {self.artist}"
    
    def save_audio_file(self, file):
        """Save audio file to database storage"""
        filename = f"{self.id}_{file.name}"
        music_storage._save(filename, file)
        self.audio_file = filename
        self.save(update_fields=['audio_file'])
    
    def save_cover_image(self, file):
        """Save cover image to database storage"""
        filename = f"{self.id}_{file.name}"
        cover_storage._save(filename, file)
        self.cover_image = filename
        self.save(update_fields=['cover_image'])
    
    @property
    def audio_url(self):
        """Get URL for audio file"""
        return music_storage.url(self.audio_file) if self.audio_file else None
    
    @property
    def cover_url(self):
        """Get URL for cover image"""
        return cover_storage.url(self.cover_image) if self.cover_image else None