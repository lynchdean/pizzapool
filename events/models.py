import re
import uuid

from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.db import models
from django import forms
from django.db.models import Sum, UniqueConstraint
from django.db.models.functions import Lower
from django.forms import ModelForm
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.template.defaultfilters import slugify
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
alphanumeric_hyphen_space = RegexValidator(
    r'^[0-9a-zA-Z\- ]*$',
    'Only alphanumeric characters, hyphens and spaces are allowed.')


class Organisation(models.Model):
    name = models.CharField(max_length=50, unique=True, validators=[alphanumeric_hyphen_space])
    description = models.CharField(max_length=200)
    logo = models.ImageField(upload_to="logos")
    path = models.SlugField(unique=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name="unique_organisation_name",
                violation_error_message="Organisation name already exists."
            ),
        ]

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        if self.name:
            self.name = ' '.join(str(self.name).split())

    def save(self, *args, **kwargs):
        self.path = slugify(self.name)
        super().save(*args, **kwargs)


class Event(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_title = models.CharField(max_length=100)
    date = models.DateTimeField("date of event")
    description = models.CharField("Description (Optional)", max_length=200, blank=True)
    servings_per_order = models.PositiveIntegerField(default=8, validators=[MinValueValidator(1)])
    private = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.organisation} - {self.date}: {'[LOCKED]' if self.locked else ''} {self.event_title}"

    def upcoming(self, organisation):
        return self.filter(organisation=organisation, start__gte=timezone.now().replace(hour=0, minute=0, second=0),
                           end__lte=timezone.now().replace(hour=23, minute=59, second=59))

    def past(self, organisation):
        return self.filter(organisation=organisation, date__lt=timezone.now())


class PizzaOrder(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    purchaser_name = models.CharField("Name", max_length=50)
    purchaser_whatsapp = PhoneNumberField("WhatsApp", null=False, blank=False)
    purchaser_revolut = models.CharField("Revolut username", max_length=16, validators=[alphanumeric])
    pizza_type = models.CharField(max_length=100)
    price_per_slice = models.DecimalField("Price per slice", max_digits=4, decimal_places=2)
    available_slices = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self) -> str:
        return f"{self.purchaser_name} - {self.pizza_type}, Event: {self.event}"

    def matched_slices(self):
        """Returns PizzaSlices linked with this order, returns empty queryset if no slices are linked"""
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

    def event_is_locked(self):
        return self.event.locked

    def _validate_available_slices_maximum(self):
        if self.available_slices >= self.event.servings_per_order:
            raise ValidationError(
                "Available slices cannot be greater than or equal to the total servings in the order.",
                code="servings gte total servings")

    def _validate_event_is_unlocked(self):
        if self.event_is_locked():
            raise ValidationError("Event is locked", code="locked")

    def clean(self):
        super().clean()
        if self.event and self.available_slices:
            if self.available_slices >= self.event.servings_per_order:
                raise ValidationError({
                    'available_slices': f"Available slices cannot be greater than or equal to "
                                        f"{self.event.servings_per_order}."
                })

    def save(self, *args, **kwargs):
        self._validate_available_slices_maximum()
        self._validate_event_is_unlocked()
        super(PizzaOrder, self).save(*args, **kwargs)


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
            if self.pizza_order.event_is_locked():
                raise ValidationError("Event is locked", code="locked")
            if self.number_of_slices > self.pizza_order.get_total_remaining():
                raise ValidationError("Insufficient remaining slices", code="insufficient_slices")
        super(PizzaSlices, self).save(*args, **kwargs)


class PizzaOrderForm(ModelForm):
    class Meta:
        model = PizzaOrder
        fields = '__all__'
        widgets = {'event': forms.HiddenInput()}
        error_messages = {
            'purchaser_whatsapp': {
                'invalid': "Enter a valid phone number (e.g. 087 123 4567) or a number with an international call prefix.",
            },
        }


class PizzaSlicesForm(ModelForm):
    class Meta:
        model = PizzaSlices
        fields = "__all__"
        widgets = {'pizza_order': forms.HiddenInput()}
        error_messages = {
            'buyer_whatsapp': {
                'invalid': "Enter a valid phone number (e.g. 087 123 4567) or a number with an international call prefix.",
            },
        }

    def __init__(self, *args, **kwargs):
        super(PizzaSlicesForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        if initial:
            remaining = initial['pizza_order'].get_total_remaining()
            self.fields['number_of_slices'].widget.attrs.update(
                {'max': remaining},
            )


class EventsAccessForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(EventsAccessForm, self).__init__(*args, **kwargs)
        self.fields.pop('username')

    def clean(self):
        super(EventsAccessForm, self).clean()
        self.user_cache = authenticate(
            self.request,
            username='events-access',
            password=self.cleaned_data.get('password')
        )
        if self.user_cache is None:
            raise forms.ValidationError('Invalid password')
