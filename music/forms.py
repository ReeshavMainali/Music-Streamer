from django import forms
from .models import Track

class TrackUploadForm(forms.ModelForm):
    """Form for uploading music tracks"""
    audio_file = forms.FileField(
        label='Audio File',
        help_text='Supported formats: MP3, WAV, OGG'
    )
    cover_image = forms.ImageField(
        label='Cover Image',
        required=False,
        help_text='Optional: Upload album art or cover image'
    )
    
    class Meta:
        model = Track
        fields = ['title', 'artist', 'album', 'genre', 'audio_file', 'cover_image']
        help_texts = {
            'audio_file': 'Supported formats: MP3, WAV, OGG',
            'cover_image': 'Optional: Upload album art or cover image',
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