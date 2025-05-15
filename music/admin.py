from django.contrib import admin
from .models import Track

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'genre', 'uploaded_by', 'upload_date')
    list_filter = ('genre', 'upload_date')
    search_fields = ('title', 'artist')
    readonly_fields = ('upload_date',)