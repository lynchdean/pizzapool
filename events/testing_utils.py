from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from .models import Event, Order, Serving, Organisation

mock_img = SimpleUploadedFile(name='test_image.png', content=b"file data")


def create_organisation(name="Test Org", description="org desc", logo=mock_img):
    return Organisation.objects.create(name=name, description=description, logo=logo)


def create_event(organisation, name="Test Event", date=timezone.now(), description="desc", servings_per_order=8,
                 locked=False):
    return Event.objects.create(organisation=organisation, name=name, date=date, description=description,
                                servings_per_order=servings_per_order, locked=locked)


def create_order(event, purchaser_name="Bob", purchaser_whatsapp="0879876543", purchaser_revolut="BobRev",
                 description="Pep", price_per_serving=4, available_servings=7):
    return Order.objects.create(event=event, purchaser_name=purchaser_name, purchaser_whatsapp=purchaser_whatsapp,
                                purchaser_revolut=purchaser_revolut, description=description,
                                price_per_serving=price_per_serving, available_servings=available_servings)


def create_serving(order, buyer_name="John", buyer_whatsapp="0871234567", number_of_servings=1):
    return Serving.objects.create(order=order, buyer_name=buyer_name, buyer_whatsapp=buyer_whatsapp,
                                  number_of_servings=number_of_servings)
