from django.db import models
import uuid

class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, auto_created=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField()
    face_encoding = models.BinaryField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Students'
        verbose_name = 'Student'

    def imageURL(self):
        try:
            url = self.photo.url
        except:
            url = ''
        return url
