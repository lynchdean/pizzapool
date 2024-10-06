from django import forms
from django.forms import FileInput, ImageField

from events.models import Organisation, PizzaOrder, PizzaSlices, Event

from .widgets import DateTimeInput


class OrgEditForm(forms.ModelForm):
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
        fields = '__all__'
        exclude = ['organisation', 'servings_per_order']


class PizzaOrderForm(forms.ModelForm):
    class Meta:
        model = PizzaOrder
        fields = '__all__'
        widgets = {'event': forms.HiddenInput()}
        error_messages = {
            'purchaser_whatsapp': {
                'invalid': "Enter a valid phone number (e.g. 087 123 4567) or a number with an international call prefix.",
            },
        }


class PizzaSlicesForm(forms.ModelForm):
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
