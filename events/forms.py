from django import forms
from django.forms import FileInput, ImageField

from events.models import Organisation, PizzaOrder, PizzaSlices, Event

from .widgets import DateTimeInput


class OrgUpdateForm(forms.ModelForm):
    logo = ImageField(widget=FileInput)

    class Meta:
        model = Organisation
        fields = ['description', 'logo']


class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'date', 'description', 'servings_per_order', 'private', 'locked']
        widgets = {
            'date': DateTimeInput(),
        }

    def __init__(self, *args, **kwargs):
        super(EventCreateForm, self).__init__(*args, **kwargs)
        self.fields['servings_per_order'].widget.attrs.update(
            {'min': 1},
        )


class EventEditForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'date', 'description', 'private', 'locked']


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = PizzaOrder
        fields = ['purchaser_name', 'purchaser_whatsapp', 'purchaser_revolut', 'pizza_type', 'price_per_slice',
                  'available_slices']
        error_messages = {
            'purchaser_whatsapp': {
                'invalid': "Enter a valid phone number (e.g. 087 123 4567) or a number with an international call prefix.",
            },
        }

    def __init__(self, *args, **kwargs):
        super(OrderCreateForm, self).__init__(*args, **kwargs)
        self.event = self.initial.get('event')
        if self.event:
            self.fields['available_slices'].widget.attrs.update(
                {'min': 1, 'max': self.event.servings_per_order - 1},
            )
        self.fields['price_per_slice'].widget.attrs.update(
            {'min': 0.01},
        )

    def clean_available_slices(self):
        available_slices = self.cleaned_data.get('available_slices')
        if self.event and available_slices > self.event.servings_per_order:
            raise forms.ValidationError("Available slices cannot be greater than the total servings in the order.")
        return available_slices


class ServingCreateForm(forms.ModelForm):
    class Meta:
        model = PizzaSlices
        fields = "buyer_name", "buyer_whatsapp", "number_of_slices"
        error_messages = {
            'buyer_whatsapp': {
                'invalid': "Enter a valid phone number (e.g. 087 123 4567) or a number with an international call prefix.",
            },
        }

    def __init__(self, *args, **kwargs):
        super(ServingCreateForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        if initial:
            remaining = initial['pizza_order'].get_total_remaining()
            self.fields['number_of_slices'].widget.attrs.update(
                {'max': remaining},
            )
