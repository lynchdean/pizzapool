import uuid

from django.db import models
from django import forms
from django.db.models import Sum
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField


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
    purchaser_name = models.CharField("Name", max_length=50)
    purchaser_whatsapp = PhoneNumberField("WhatsApp", null=False, blank=False)
    purchaser_revolut = models.CharField("Revolut", max_length=50)
    pizza_type = models.CharField(max_length=100)
    price_per_slice = models.DecimalField("Price per slice", max_digits=4, decimal_places=2)
    available_slices = models.PositiveIntegerField(default=1, validators=[
        MinValueValidator(1),
        MaxValueValidator(8)])

    def __str__(self) -> str:
        return f"{self.purchaser_name} - {self.pizza_type}, Event: {self.event}"

    def matched_slices(self):
        """Returns PizzaSlices linked with this order, returns None if no slices are linked"""
        return PizzaSlices.objects.filter(pizza_order=self.id)

    def get_total_claimed(self) -> int:
        """Returns the number of slices linked with this order"""
        matched_slices = self.matched_slices()
        if matched_slices:
            return matched_slices.aggregate(Sum('number_of_slices'))['number_of_slices__sum']
        else:
            return 0

    def get_total_remaining(self):
        """Returns the number of slices that have not been claimed from the order"""
        return self.available_slices - self.get_total_claimed()


class PizzaSlices(models.Model):
    pizza_order = models.ForeignKey(PizzaOrder, on_delete=models.CASCADE)
    buyer_name = models.CharField("Name", max_length=50)
    buyer_whatsapp = PhoneNumberField("WhatsApp", null=False, blank=False)
    number_of_slices = models.PositiveIntegerField(default=1, validators=[
        MinValueValidator(1),
        MaxValueValidator(8)])

    def __str__(self) -> str:
        return f"{self.buyer_name}"

    def save(self, *args, **kwargs):
        if self.id is None:
            if self.number_of_slices > self.pizza_order.get_total_remaining():
                return False
        return super(PizzaSlices, self).save(*args, **kwargs)


class PizzaOrderForm(ModelForm):
    class Meta:
        model = PizzaOrder
        fields = '__all__'
        widgets = {'event': forms.HiddenInput()}


class PizzaSlicesForm(ModelForm):
    class Meta:
        model = PizzaSlices
        fields = "__all__"
        widgets = {'pizza_order': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(PizzaSlicesForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        if initial:
            remaining = initial['pizza_order'].get_total_remaining()
            self.fields['number_of_slices'].widget.attrs.update(
                {'max': remaining},
            )
