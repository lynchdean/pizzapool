from django import forms


class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"
