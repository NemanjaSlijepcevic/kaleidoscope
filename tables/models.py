from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from .imagekit_processors import TextWatermark


class Author(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Place(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Year(models.Model):
    name = models.IntegerField(unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return str(self.name)


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Image(models.Model):
    author = models.ManyToManyField(Author, blank=True, db_index=True)
    title = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='gallery/')
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(360, 360)],
        format='JPEG',
        options={'quality': 80}
    )
    watermarked = ImageSpecField(
        source='image',
        processors=[TextWatermark()],
        format='JPEG',
        options={'quality': 90}
    )
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    category = models.ManyToManyField(Category, blank=True, db_index=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name='image_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        default=1,
        blank=True,
        null=True,
        related_name='image_edited'
    )

    class Meta:
        ordering = ('author__name', 'title')

    def __str__(self):
        author_names = ', '.join([author.name for author in self.author.all()][:3])
        if self.author.count() > 3:
            author_names += '...'
        return f"{author_names}: {self.title}"

    def get_absolute_url(self):
        return reverse("images:image-update", kwargs={"pk": self.id})
