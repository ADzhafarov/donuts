# Generated by Django 4.2.6 on 2023-10-20 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagrams', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='molecules',
            name='license_plate',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='molecules',
            name='name',
            field=models.CharField(max_length=75),
        ),
        migrations.AlterField(
            model_name='molecules',
            name='rna_type',
            field=models.CharField(max_length=25),
        ),
    ]
