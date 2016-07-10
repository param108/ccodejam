from django.db import models

# Create your models here.
class admin_users(models.Model):
    username=models.CharField(max_length=100,unique=True)
    is_staff=models.BooleanField(default=False)

