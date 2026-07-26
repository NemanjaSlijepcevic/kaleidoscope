from django.conf import settings
from PIL import Image, ImageDraw, ImageFont


class TextWatermark:
    def __init__(self, text=getattr(settings, 'IMAGE_WATERMARK_TEXT', 'WATERMARK'),
                 opacity=getattr(settings, 'IMAGE_WATERMARK_OPACITY', 80)):
        self.text = text
        self.opacity = opacity

    def process(self, image):
        # Ensure image is in RGBA to handle transparency
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        txt_layer = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # 1. Determine Target Height (50% of image height)
        target_height = image.height * getattr(settings, 'IMAGE_WATERMARK_SCALE', 0.5)

        # 2. Load font and scale it
        # You may need to adjust the path to a .ttf file on your system
        font_path = getattr(settings, 'WATERMARK_FONT_PATH',
                            f"{settings.MEDIA_ROOT}/fonts/DejaVuSans-Bold.ttf")

        # Start with a default size and scale up/down to match target_height
        font_size = 1
        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError as exc:
            # Failing here means every watermarked image silently 404s, and the
            # cause ("cannot open resource") gives no hint which resource. Don't
            # fall back to an unwatermarked image: the watermark is the reason
            # originals aren't served in the first place.
            raise OSError(
                f"Watermark font not found at {font_path!r}. The font lives under "
                f"MEDIA_ROOT, which .dockerignore excludes, so a container needs "
                f"either a mounted media/fonts/ or a WATERMARK_FONT_PATH override."
            ) from exc

        # Quickly approximate the correct font size
        # We use font.getbbox to get the precise dimensions of the rendered text
        left, top, right, bottom = font.getbbox(self.text)
        current_text_height = bottom - top

        if current_text_height > 0:
            font_size = int(target_height * (font_size / current_text_height))
            font = ImageFont.truetype(font_path, font_size)

        # 3. Calculate position (Centered)
        left, top, right, bottom = font.getbbox(self.text)
        text_width = right - left
        text_height = bottom - top

        x = (image.width - text_width) // 2
        y = (image.height - text_height) // 2

        # 4. Draw the text with opacity
        # Fill color: (R, G, B, A)
        draw.text((x, y), self.text, font=font, fill=(255, 255, 255, self.opacity))

        # Composite the watermark layer over the original image
        out = Image.alpha_composite(image, txt_layer)

        # Convert back to RGB if you don't need transparency in the final file
        return out.convert('RGB')
