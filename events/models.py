import uuid

from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_title = models.CharField(max_length=100)
    date = models.DateTimeField("date of event")
    description = models.CharField(max_length=200)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.event_title} - {self.date}"

    
class PizzaOrder(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    purchaser_name = models.CharField(max_length=50)
    purchaser_whatsapp = models.CharField(max_length=50)
    purchaser_revolut = models.CharField(max_length=50)
    pizza_type = models.CharField(max_length=100)
    available_slices = models.PositiveIntegerField(default=1,validators=[
        MinValueValidator(1),
        MaxValueValidator(8)])

    def __str__(self) -> str:
        return f"{self.purchaser_name} - {self.pizza_type}"


class PizzaSlices(models.Model):
    pizza_order = models.ForeignKey(PizzaOrder, on_delete=models.CASCADE)
    buyer_name = models.CharField(max_length=50)
    buyer_whatsapp = models.CharField(max_length=50)
    number_of_slices = models.PositiveIntegerField(default=1,validators=[
        MinValueValidator(1),
        MaxValueValidator(8)])
    
    def __str__(self) -> str:
        return self.buyer_name


class PizzaOrderForm(ModelForm):
    class Meta:
        model = PizzaOrder
        fields = '__all__'

class PizzaSlicesForm(ModelForm):
    class Meta:
        model = PizzaSlices
        fields = "__all__"

