from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.db import models
from io import BytesIO

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
        instance = self.model.objects.get(name=name)
        file_content = instance.data
        content_file = ContentFile(file_content)
        content_file.name = name
        return content_file
    
    def _save(self, name, content):
        """Save the file to the database"""
        content_type = getattr(content, 'content_type', '')
        content.seek(0)
        data = content.read()
        size = len(data)
        
        # Create or update the database entry
        self.model.objects.create(
            name=name,
            data=data,
            **{self.content_type_field: content_type, self.size_field: size}
        )
        return name
    
    def exists(self, name):
        """Check if a file with this name already exists"""
        return self.model.objects.filter(name=name).exists()
    
    def delete(self, name):
        """Delete the file"""
        self.model.objects.filter(name=name).delete()
    
    def url(self, name):
        """Return URL for accessing the file"""
        return f'/media/db/{self.model.__name__.lower()}/{name}'
    
    def size(self, name):
        """Return the size of the file"""
        return self.model.objects.get(name=name).size