import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, UniqueConstraint
from django.db.models.functions import Lower
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.template.defaultfilters import slugify
from django.utils import timezone
from django_sqids import SqidsField
from phonenumber_field.modelfields import PhoneNumberField
from sqids import Sqids

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


class OrgUser(AbstractUser):
    organisation = models.ForeignKey(Organisation, null=True, on_delete=models.SET_NULL)
    contact = PhoneNumberField("Phone/WhatsApp", null=False, blank=True)

    def __str__(self):
        return f"{'[ADMIN] ' if self.is_superuser else ''}{self.username}"


class Event(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    slug = SqidsField(real_field_name="id", min_length=10, unique=True)
    name = models.CharField(max_length=100)
    date = models.DateTimeField("date of event")
    description = models.CharField("Description (Optional)", max_length=200, blank=True)
    servings_per_order = models.PositiveIntegerField("Servings per order (Cannot be changed later)", default=8,
                                                     validators=[MinValueValidator(1)])
    private = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.organisation} - {self.date}: {'[LOCKED]' if self.locked else ''} {self.name}"

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
        return f"{self.purchaser_name} - {self.pizza_type}"

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
