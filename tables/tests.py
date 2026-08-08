"""Search normalisation and gallery search.

The collection is stored in Serbian Cyrillic and searched in whatever the
visitor types. These cover the three things that were broken, and the rules
that keep them working.
"""

import io
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from django.test import TestCase, override_settings
from PIL import Image as PilImage

from .models import Author, Category, Image, Place, Year
from .search import AZBUKA, fold, sort_key


def a_real_image(name="x.jpg"):
    """Saving an Image generates its thumbnail, so the source must exist.

    A 1x1 JPEG is enough and keeps the tests off any fixture file.
    """
    buffer = io.BytesIO()
    PilImage.new("RGB", (1, 1), "white").save(buffer, format="JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


class FoldTests(TestCase):
    """The reduction itself, independent of the database."""

    def test_lowercases_cyrillic(self):
        # SQLite's own lower() is ASCII-only, which is why this has to happen
        # in Python before anything reaches the database.
        self.assertEqual(fold("ДУЧИЋ"), fold("дучић"))

    def test_cyrillic_and_latin_meet(self):
        for latin in ("Dučić", "DUCIC", "ducic"):
            self.assertEqual(fold(latin), fold("Дучић"), latin)

    def test_digraph_spelled_either_way(self):
        """њ is one letter but can be typed as н + ј; both must agree."""
        self.assertEqual(fold("Његош"), fold("Нјегош"))
        self.assertEqual(fold("Његош"), fold("njegoš"))
        self.assertEqual(fold("Његош"), fold("NJEGOS"))
        self.assertEqual(fold("Љубиње"), fold("Лјубиње"))
        self.assertEqual(fold("Џак"), fold("Джак"))

    def test_diacritics_stripped(self):
        self.assertEqual(fold("Дучић"), "ducic")
        self.assertEqual(fold("Ђурић"), "djuric")
        self.assertEqual(fold("Џак"), "dzak")

    def test_whitespace_collapsed(self):
        self.assertEqual(fold("Нови  Сад"), fold("Novi Sad"))

    def test_handles_empty_and_none(self):
        self.assertEqual(fold(None), "")
        self.assertEqual(fold(""), "")
        self.assertEqual(fold("   "), "")

    def test_is_idempotent(self):
        """Folding an already-folded string must not change it further."""
        for text in ("Његош", "Дучић, Нићифор", "Гатачко поље"):
            self.assertEqual(fold(fold(text)), fold(text), text)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class SearchKeyTests(TestCase):
    """The stored copy is derived, and stays derived."""

    @classmethod
    def setUpTestData(cls):
        # Book.created_by/edited_by default to user 1, which does not exist in
        # an isolated test database.
        cls.user = User.objects.create_user("t")

    def test_populated_on_create(self):
        self.assertEqual(Author.objects.create(name="Његош").search_key, "njegos")

    def test_rewritten_on_rename(self):
        author = Author.objects.create(name="Његош")
        author.name = "Дучић"
        author.save()
        author.refresh_from_db()
        self.assertEqual(author.search_key, "ducic")

    def test_image_normalises_its_title(self):
        image = Image.objects.create(title="Њиве и катуни", image=a_real_image(),
                                     created_by=self.user, edited_by=self.user)
        self.assertEqual(image.search_key, "njive i katuni")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class GallerySearchTests(TestCase):
    """End to end through the queryset the list view builds."""

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user("t")
        cls.image = Image.objects.create(
            title="Његош на Ловћену", image=a_real_image("a.jpg"),
            place=Place.objects.create(name="Нови Сад"),
            year=Year.objects.create(name=1977),
            created_by=user, edited_by=user,
        )
        cls.image.author.add(Author.objects.create(name="Ђурић, Владан"))
        cls.image.category.add(Category.objects.create(name="Споменици"))

        other = Image.objects.create(title="Гатачко поље", image=a_real_image("b.jpg"),
                                     created_by=user, edited_by=user)
        other.author.add(Author.objects.create(name="Дучић, Нићифор"))

    def search(self, text):
        key = fold(text)
        if not key:
            return Image.objects.none()
        return Image.objects.filter(
            Q(search_key__contains=key)
            | Q(author__search_key__contains=key)
            | Q(category__search_key__contains=key)
            | Q(place__search_key__contains=key)
            | Q(year__name__icontains=text)
        ).distinct()

    def assertFinds(self, query, title):
        self.assertIn(title, [i.title for i in self.search(query)],
                      f"{query!r} should find {title!r}")

    def test_cyrillic_is_case_insensitive(self):
        for query in ("његош", "ЊЕГОШ", "Његош"):
            self.assertFinds(query, "Његош на Ловћену")

    def test_latin_query_finds_cyrillic_record(self):
        for query in ("njegos", "Njegoš", "NJEGOŠ"):
            self.assertFinds(query, "Његош на Ловћену")

    def test_digraph_typed_as_two_letters(self):
        self.assertFinds("нјегош", "Његош на Ловћену")

    def test_matches_related_fields(self):
        self.assertFinds("djuric", "Његош на Ловћену")     # author, ASCII
        self.assertFinds("novi sad", "Његош на Ловћену")   # place
        self.assertFinds("spomenici", "Његош на Ловћену")  # category

    def test_year_still_searchable(self):
        self.assertFinds("1977", "Његош на Ловћену")

    def test_does_not_match_everything(self):
        self.assertFalse(self.search("zzzzz").exists())

    def test_narrows_rather_than_widens(self):
        """A query matching one record must not return the other."""
        titles = [i.title for i in self.search("ducic")]
        self.assertIn("Гатачко поље", titles)
        self.assertNotIn("Његош на Ловћену", titles)


class CollationTests(TestCase):
    """Serbian alphabet order, which is not code-point order."""

    def test_azbuka_sorts_into_itself(self):
        self.assertEqual(sorted(AZBUKA, key=sort_key), list(AZBUKA))

    def test_serbian_letters_no_longer_jump_the_queue(self):
        """ђ ј љ њ ћ џ live below А in Unicode; they must not sort there."""
        names = ["Ђурић", "Његош", "Аврамовић", "Љубић", "Бабић",
                 "Џаковић", "Ћирић", "Јовановић", "Зец", "Шаровић"]
        self.assertEqual(
            sorted(names, key=sort_key),
            ["Аврамовић", "Бабић", "Ђурић", "Зец", "Јовановић",
             "Љубић", "Његош", "Ћирић", "Џаковић", "Шаровић"],
        )

    def test_case_does_not_split_the_list(self):
        self.assertEqual(sort_key("АВРАМОВИЋ"), sort_key("аврамовић"))

    def test_letters_that_the_search_key_merges_still_sort_apart(self):
        """Ж and З both fold to "z" for matching, but must not collate equal."""
        self.assertEqual(fold("ж"), fold("з"))
        self.assertLess(sort_key("ж"), sort_key("з"))
        self.assertLess(sort_key("и"), sort_key("ј"))
        self.assertLess(sort_key("ћ"), sort_key("ч"))

    def test_digits_and_spaces_sort_before_letters(self):
        self.assertLess(sort_key("1968"), sort_key("Аврамовић"))
        self.assertLess(sort_key("Нови Сад"), sort_key("Нови­сад".replace("\u00ad", "")))

    def test_database_orders_in_serbian(self):
        for name in ["Ђурић", "Његош", "Аврамовић", "Џаковић", "Бабић"]:
            Author.objects.create(name=name)
        self.assertEqual(
            [a.name for a in Author.objects.all()],
            ["Аврамовић", "Бабић", "Ђурић", "Његош", "Џаковић"],
        )

    def test_sort_key_rewritten_on_rename(self):
        author = Author.objects.create(name="Шаровић")
        author.name = "Аврамовић"
        author.save()
        author.refresh_from_db()
        self.assertEqual(author.sort_key, sort_key("Аврамовић"))
