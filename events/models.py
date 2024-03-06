import uuid

from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_title = models.CharField(max_length=100)
    date = models.DateTimeField("date of event")
    description = models.CharField(max_length=200)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.event_title

    
class Vehicle(models.Model):
    driver_name = models.CharField(max_length=50)
    driver_contact = models.CharField(max_length=50)
    meeting_place = models.CharField(max_length=200)
    date = models.DateTimeField("")
    notes = models.CharField(max_length=200)
    
    def __str__(self) -> str:
        return self.driver_name


class Passenger(models.Model):
    passenger_name = models.CharField(max_length=50)
    passenger_contact = models.CharField(max_length=50)
    
    def __str__(self) -> str:
        return self.passenger_name