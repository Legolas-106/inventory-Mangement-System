from django.db import models
from datetime import timedelta
from django.utils import timezone

# Create your models here.

class ItemModel(models.Model):

    CATEGORY_TYPES = [
        ('food','food'),
        ('drinks','drinks'),
        ('cleaning_essentials','cleaning_essentials'),
        ('cloths','cloths'),
        ('electronic','electronic'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000,blank=True)
    category = models.CharField(choices = CATEGORY_TYPES)
    stock_in_time = models.DateField(null=False, blank=True)
    expiry_time = models.DateField(null=False,blank=True)

    
    def save(self, *args, **kwargs):
        # Set stock_in_time to the current time if not provided
        # print("Inside save method",self)

        if not self.stock_in_time:
            self.stock_in_time = timezone.now().date()

        # Dynamically set expiry_time based on category if not provided
        if not self.expiry_time:
            if self.category == 'food':
                self.expiry_time = self.stock_in_time + timedelta(days=15)
            elif self.category == 'cleaning_essentials':
                self.expiry_time = self.stock_in_time + timedelta(days=365)
            elif self.category == 'electronic':
                self.expiry_time = self.stock_in_time + timedelta(days=730)
            elif self.category == 'drinks':
                self.expiry_time = self.stock_in_time + timedelta(days=30)
            elif self.category == 'cloths':
                self.expiry_time = self.stock_in_time + timedelta(days=1825)

            if self.expiry_time is None:
                raise ValueError("Expiry time must be set based on the category.")

        # Call the original save method
        super(ItemModel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

