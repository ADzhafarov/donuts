from django.db import models

class datasets(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)