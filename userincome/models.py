from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.


class UserIncome(models.Model):
    amount = models.FloatField()  # DECIMAL
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    source = models.CharField(max_length=266)
    versements = models.CharField(max_length=200, default='Paypal')
    categories = models.CharField(max_length=266)



    def __str__(self):
        return self.source

    class Meta:
        ordering: ['-date']



class Categories(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name



class Source(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Versements(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Modes de versement' 

    def __str__(self):
        return self.name
