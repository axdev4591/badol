from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.


class Expense(models.Model):

    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE) #delete on cascade, means delete all action of the user when the user is deleted
    category = models.CharField(max_length=266)
    payment = models.CharField(max_length=200, default='Cash')


    

    class Meta:
        ordering: ['-date'] #order by date in descending order
        verbose_name_plural = 'Dépenses' 

    def __str__(self):
        return self.category


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Categories' #define in djando admin how this model should be called in plural 

    def __str__(self):
        return self.name


class Payment(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Modes de paiement' #define in djando admin how this model should be called in plural

    def __str__(self):
        return self.name
