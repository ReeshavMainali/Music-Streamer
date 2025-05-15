from django import forms
from .models import Track
from users.models import Genre
from mutagen.mp3 import MP3
import mutagen

class TrackUploadForm(forms.ModelForm):
    """Form for uploading music tracks"""
    class Meta:
        model = Track
        fields = ['title', 'artist', 'genre', 'audio_file', 'cover_image']
        widgets = {
            'genre': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_audio_file(self):
        """Validate that the uploaded file is an audio file and extract its duration"""
        audio_file = self.cleaned_data.get('audio_file')
        if audio_file:
            if not audio_file.name.endswith(('.mp3', '.wav', '.ogg')):
                raise forms.ValidationError('Unsupported file format. Please upload MP3, WAV, or OGG files.')
            
            # Try to get the duration of the track
            try:
                audio = MP3(audio_file)
                self.instance.duration = int(audio.info.length)
            except (mutagen.MutagenError, AttributeError):
                # If we can't determine the duration, we'll leave it as None
                pass
                
        return audio_file