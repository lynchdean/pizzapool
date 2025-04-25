from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, UniqueConstraint
from django.db.models.functions import Lower
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.conf import settings
from django_sqids import SqidsField
from phonenumber_field.modelfields import PhoneNumberField
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
alphanumeric_hyphen_space = RegexValidator(
    r'^[0-9a-zA-Z\- ]*$',
    'Only alphanumeric characters, hyphens and spaces are allowed.')


class Organisation(models.Model):
    name = models.CharField(max_length=50, unique=True, validators=[alphanumeric_hyphen_space])
    description = models.CharField(max_length=200)
    logo = models.ImageField(upload_to="logos")
    path = models.SlugField(unique=True)
    stripe_account_id = models.CharField(max_length=255, blank=True)
    stripe_account_verified = models.BooleanField(default=False)

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


class Order(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField("Your Name", max_length=50)
    whatsapp = PhoneNumberField("WhatsApp", null=False, blank=False)
    revolut = models.CharField("Revolut username", max_length=16, validators=[alphanumeric])
    description = models.CharField("Food description (e.g. Pizza type)", max_length=100)
    serving_price = models.DecimalField("Price of individual serving", max_digits=4, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.name} - {self.description}"

    def get_servings(self):
        """Returns Servings linked with this order, returns empty queryset if no slices are linked"""
        return Serving.objects.filter(order=self.id)

    def event_is_locked(self):
        return self.event.locked

    def _validate_event_is_unlocked(self):
        if self.event_is_locked():
            raise ValidationError("Event is locked", code="locked")

    def save(self, *args, **kwargs):
        self._validate_event_is_unlocked()
        super(Order, self).save(*args, **kwargs)


class Serving(models.Model):
    STATUS_CHOICES = (
        ('unclaimed', 'Unclaimed'),
        ('reserved', 'Reserved'),
        ('claimed', 'Claimed'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    name = models.CharField("Name", max_length=50, blank=True)
    whatsapp = PhoneNumberField("WhatsApp", null=True, blank=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unclaimed')

    def __str__(self) -> str:
        if self.status == 'unclaimed':
            return f"Unclaimed ({self.order})"
        return f"{self.name} ({self.order})"

    def save(self, *args, **kwargs):
        """Prevent new order creation if the Event is locked"""
        if self.id is None and self.order.event_is_locked():
            raise ValidationError("Event is locked", code="locked")
        super(Serving, self).save(*args, **kwargs)
