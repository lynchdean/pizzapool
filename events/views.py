from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the events index.")

def event(requset, event_id):
    return HttpResponse("Event: %s." % event_id)

