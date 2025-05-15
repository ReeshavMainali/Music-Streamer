from django.db import models
from django.utils import timezone
from users.models import CustomUser, Genre

class Track(models.Model):
    """Model for storing music track information"""
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, related_name='tracks')
    audio_file = models.FileField(upload_to='tracks/')
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    duration = models.PositiveIntegerField(help_text="Duration in seconds", null=True, blank=True)
    upload_date = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploaded_tracks')
    
    def __str__(self):
        return f"{self.title} - {self.artist}"
    
    class Meta:
        ordering = ['-upload_date']