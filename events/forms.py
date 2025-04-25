from django import forms
from django.core.validators import MaxValueValidator
from django.forms import FileInput, ImageField

from events.models import Organisation, Order, Serving, Event

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
    reserved_servings = forms.IntegerField(
        label="How many servings do you want to claim for yourself?",
        min_value=0,
        initial=1,
        required=True,
        help_text="Number of servings you want to keep for yourself"
    )

    class Meta:
        model = Order
        fields = ['name', 'whatsapp', 'revolut', 'description', 'serving_price']
        error_messages = {
            'whatsapp': {
                'invalid': "Enter a valid phone number (e.g. 087 123 4567) or a number with an international call prefix.",
            },
        }

    def __init__(self, *args, **kwargs):
        super(OrderCreateForm, self).__init__(*args, **kwargs)
        self.event = self.initial.get('event')

        # Set the max value for reserved_servings based on event settings
        if self.event:
            max_servings = self.event.servings_per_order
            self.fields['reserved_servings'].validators.append(MaxValueValidator(max_servings))
            self.fields['reserved_servings'].help_text = f"Maximum {max_servings} serving(s) available"

    def clean_reserved_servings(self):
        reserved_servings = self.cleaned_data.get('reserved_servings')
        if self.event and reserved_servings > self.event.servings_per_order:
            raise forms.ValidationError(f"You cannot claim more than {self.event.servings_per_order} servings.")
        return reserved_servings


class ServingCreateForm(forms.ModelForm):
    class Meta:
        model = Serving
        fields = "name", "whatsapp"
        error_messages = {
            'whatsapp': {
                'invalid': "Enter a valid phone number (e.g. 087 123 4567) or a number with an international call prefix.",
            },
        }

    def __init__(self, *args, **kwargs):
        super(ServingCreateForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        if initial:
            self.order = initial.get('order')
            remaining = self.order.get_total_remaining()
            self.fields['number_of_servings'].widget.attrs.update(
                {'max': remaining, 'min': 1}
            )
            self.fields['number_of_servings'].help_text = f"Maximum {remaining} serving(s) available"
