from django.conf import settings


def embed(request):
    """Expose the embedding parent's origin to templates.

    Both apps are shown inside an iframe on the Ghost site. The frame needs the
    parent's origin for two things: to post its height to a known target rather
    than to "*", and to decide whose theme/script preferences to accept.
    """
    return {"embed_parent_origin": settings.EMBED_PARENT_ORIGIN}
