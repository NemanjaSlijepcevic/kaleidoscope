from django.apps import AppConfig


class TablesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tables'

    def ready(self):
        # Phone uploads and interrupted transfers routinely produce JPEGs with a
        # few bytes missing at the end. Pillow refuses those with
        # "image file is truncated", which made both derived images fail and left
        # the card blank. Render what is there instead.
        from PIL import ImageFile
        ImageFile.LOAD_TRUNCATED_IMAGES = True
