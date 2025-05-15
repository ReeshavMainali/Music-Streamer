from django.contrib import admin
from .models import Track, MusicFile, CoverImage

class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'genre', 'uploaded_by', 'upload_date')
    search_fields = ('title', 'artist', 'album')
    list_filter = ('genre', 'upload_date')
    
    def save_model(self, request, obj, form, change):
        """Override save_model to handle file storage in database"""
        # First save the model to get an ID if it's a new track
        super().save_model(request, obj, form, change)
        
        # Handle audio file
        if 'audio_file' in form.files:
            audio_file = form.files['audio_file']
            obj.save_audio_file(audio_file)
        
        # Handle cover image
        if 'cover_image' in form.files:
            cover_image = form.files['cover_image']
            obj.save_cover_image(cover_image)

# Register models with admin site
admin.site.register(Track, TrackAdmin)
admin.site.register(MusicFile)
admin.site.register(CoverImage)