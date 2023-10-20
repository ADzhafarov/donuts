from django.db import models

class Datasets(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Molecules(models.Model):
    dataset = models.CharField(max_length=50, db_index=True)
    rna_type = models.CharField(max_length=25)
    length = models.IntegerField()
    name = models.CharField(max_length=75)
    license_plate = models.CharField(max_length=100)
    unnormalized_read_counts = models.IntegerField()
    
    class Meta:
        unique_together = ('dataset', 'license_plate',)