from django.db import models


class Student(models.Model):
    school_id = models.CharField(max_length=11, unique=True)
    password = models.CharField(max_length=32)
    name = models.CharField(max_length=32)
    email = models.EmailField(max_length=32)
    
    def __str__(self):
        return self.name
    
