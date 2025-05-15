from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.db import models
from django.utils.deconstruct import deconstructible
from io import BytesIO
import os

class DatabaseFileModel(models.Model):
    """Model to store files in the database"""
    name = models.CharField(max_length=255)
    data = models.BinaryField()
    content_type = models.CharField(max_length=100, blank=True)
    size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True

class MusicFile(DatabaseFileModel):
    """Model to store music files"""
    pass

class CoverImage(DatabaseFileModel):
    """Model to store cover images"""
    pass

@deconstructible
class DatabaseStorage(Storage):
    """Custom storage backend that stores files in the database"""
    
    def __init__(self, model=None, content_type_field='content_type', 
                 size_field='size', *args, **kwargs):
        self.model = model
        self.content_type_field = content_type_field
        self.size_field = size_field
        super().__init__(*args, **kwargs)
    
    def _open(self, name, mode='rb'):
        """Retrieve the file from the database"""
        # Extract the actual filename without the path
        filename = os.path.basename(name)
        instance = self.model.objects.get(name=filename)
        file_content = instance.data
        content_file = ContentFile(file_content)
        content_file.name = name
        return content_file
    
    def _save(self, name, content):
        """Save the file to the database"""
        # Extract the actual filename without the path
        filename = os.path.basename(name)
        content_type = getattr(content, 'content_type', '')
        content.seek(0)
        data = content.read()
        size = len(data)
        
        # Create or update the database entry
        self.model.objects.create(
            name=filename,
            data=data,
            **{self.content_type_field: content_type, self.size_field: size}
        )
        return name
    
    def exists(self, name):
        """Check if a file with this name already exists"""
        filename = os.path.basename(name)
        return self.model.objects.filter(name=filename).exists()
    
    def delete(self, name):
        """Delete the file"""
        filename = os.path.basename(name)
        self.model.objects.filter(name=filename).delete()
    
    def url(self, name):
        """Return URL for accessing the file"""
        filename = os.path.basename(name)
        model_name = self.model.__name__.lower()
        return f'/media/db/{model_name}/{filename}'
    
    def size(self, name):
        """Return the size of the file"""
        filename = os.path.basename(name)
        return self.model.objects.get(name=filename).size
        
    def get_available_name(self, name, max_length=None):
        """Return a filename that's free on the target storage system"""
        # If the filename already exists, add a suffix to make it unique
        filename = os.path.basename(name)
        dir_name = os.path.dirname(name)
        
        name_without_extension, extension = os.path.splitext(filename)
        count = 0
        
        while self.exists(os.path.join(dir_name, filename)):
            count += 1
            filename = f"{name_without_extension}_{count}{extension}"
            
        return os.path.join(dir_name, filename)
        
    def path(self, name):
        """
        This is needed for Django's FileField but we don't have a real path
        since files are stored in the database
        """
        raise NotImplementedError("Database storage doesn't support path")