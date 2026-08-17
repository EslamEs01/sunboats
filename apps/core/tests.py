from io import BytesIO
from pathlib import Path

from django.contrib.staticfiles import finders
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from apps.core.models import ContactMessage, Settings
from apps.exhibitions.models import Exhibition, ExhibitionProgram, ExhibitionRequest
from apps.works.models import Artist, Artwork

FORBIDDEN = (
    "ArtMart",
    "artmart",
    "/shop",
    "/cart",
    "/checkout",
    "California",
    "boat tour",
    "coastal gallery",
    "Boat Tours",
)


def tiny_jpeg(color=(180, 120, 80)):
    buffer = BytesIO()
    Image.new("RGB", (40, 40), color).save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile("work.jpg", buffer.read(), content_type="image/jpeg")


class SeededSiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_sunboats")

    def _page(self, name, **kwargs):
        return self.client.get(reverse(name, kwargs=kwargs or None))

    def test_routes_resolve(self):
        self.assertEqual(reverse("home"), "/")
        self.assertEqual(reverse("exhibitions"), "/exhibitions/")
        self.assertEqual(reverse("submit"), "/submit/")
        self.assertEqual(reverse("about"), "/about/")
        self.assertEqual(reverse("gallery"), "/gallery/")
        self.assertEqual(reverse("admin:index"), "/admin/")
        sixth = Exhibition.objects.get(slug="6th-symposium-egypts-gift-2026")
        self.assertEqual(reverse("exhibition-detail", kwargs={"slug": sixth.slug}), f"/exhibitions/{sixth.slug}/")

    def test_seeded_domain(self):
        settings = Settings.objects.get(pk=1)
        self.assertEqual(settings.email, "esmaelbakr28@gmail.com")
        titles = set(Exhibition.objects.values_list("title", flat=True))
        self.assertTrue(any("7th" in t for t in titles))
        self.assertTrue(any("Egypt" in t and "Gift" in t for t in titles))
        self.assertTrue(any("5th" in t for t in titles))
        self.assertTrue(any("Minya" in t or "4th" in t for t in titles))
        sixth = Exhibition.objects.get(slug="6th-symposium-egypts-gift-2026")
        kinds = set(sixth.program_items.values_list("kind", flat=True))
        self.assertGreaterEqual(sixth.program_items.count(), 4)
        self.assertIn(ExhibitionProgram.KIND_WORKSHOP, kinds)
        self.assertIn(ExhibitionProgram.KIND_VISIT, kinds)
        self.assertIn(ExhibitionProgram.KIND_SHOW, kinds)
        self.assertGreaterEqual(Artist.objects.count(), 2)
        self.assertTrue(Artwork.objects.filter(exhibition=sixth).exists())

    def _assert_clean_public(self, response, *needles):
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        for needle in needles:
            self.assertIn(needle, html)
        lower = html.lower()
        for bad in FORBIDDEN:
            self.assertNotIn(bad.lower(), lower)

    def test_home_story(self):
        response = self._page("home")
        self._assert_clean_public(
            response,
            "Sun Boats",
            "pyramids",
            "Submit your work",
            "Egypt",
        )
        self.assertContains(response, reverse("submit"))
        self.assertContains(response, reverse("exhibitions"))

    def test_exhibitions_upcoming_before_past(self):
        response = self._page("exhibitions")
        self._assert_clean_public(response, "Upcoming", "Past")
        html = response.content.decode()
        self.assertLess(html.find("Upcoming"), html.find("Past"))
        self.assertContains(response, "7th International Symposium")
        self.assertContains(response, "Minya")

    def test_exhibition_detail_holds_program(self):
        response = self._page("exhibition-detail", slug="6th-symposium-egypts-gift-2026")
        self._assert_clean_public(
            response,
            "Gift to the World",
            "Opening workshop",
            "Pyramids visit",
            "Nile crossing",
            "Closing show",
            "Giza",
        )
        self.assertNotContains(response, "/events/")
        self.assertContains(response, reverse("submit"))

    def test_submit_fields_and_email(self):
        response = self._page("submit")
        self._assert_clean_public(response, "esmaelbakr28@gmail.com")
        for field in ("name", "email", "phone", "country", "title", "medium", "description", "image"):
            self.assertContains(response, f'name="{field}"')

    def test_submit_creates_pending_request(self):
        response = self.client.post(
            reverse("submit"),
            {
                "name": "Mona Farid",
                "email": "mona@example.com",
                "phone": "+201111111111",
                "country": "Egypt",
                "title": "Sand Wall",
                "medium": "Oil",
                "description": "A study of plateau light.",
                "image": tiny_jpeg(),
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        req = ExhibitionRequest.objects.get(title="Sand Wall")
        self.assertEqual(req.status, ExhibitionRequest.STATUS_PENDING)
        self.assertEqual(req.email, "mona@example.com")
        self.assertTrue(req.image)

    def test_about_founder_and_contact(self):
        response = self._page("about")
        self._assert_clean_public(response, "Ismail Bakr", "Esmael Bakr", "esmaelbakr28@gmail.com")
        self.assertContains(response, 'name="message"')

    def test_about_contact_persists(self):
        response = self.client.post(
            reverse("about"),
            {
                "name": "Karim",
                "email": "karim@example.com",
                "message": "I would like to visit the next edition.",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ContactMessage.objects.filter(email="karim@example.com", message__contains="next edition").exists()
        )

    def test_gallery_and_admin(self):
        gallery = self._page("gallery")
        self._assert_clean_public(gallery, "Sun Boats")
        admin = self.client.get(reverse("admin:index"), follow=True)
        self.assertEqual(admin.status_code, 200)

    def test_request_approve_reject(self):
        req = ExhibitionRequest.objects.create(
            name="Test Artist",
            email="a@example.com",
            phone="1",
            country="Italy",
            title="Night Linen",
            medium="Ink",
            description="Line study.",
            image=tiny_jpeg((40, 40, 40)),
        )
        req.approve()
        req.refresh_from_db()
        self.assertEqual(req.status, ExhibitionRequest.STATUS_APPROVED)
        req.reject()
        req.refresh_from_db()
        self.assertEqual(req.status, ExhibitionRequest.STATUS_REJECTED)

    def test_compiled_tailwind_not_bootstrap(self):
        path = finders.find("css/app.css")
        self.assertTrue(path)
        css = Path(path).read_text()
        self.assertIn("--color-paper", css)
        self.assertIn("terracotta", css.lower())
        self.assertNotIn("bootstrap", css.lower())

    def test_no_removed_routes(self):
        for url in ("/shop/", "/cart/", "/checkout/", "/products/", "/events/", "/collection/"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404, url)
