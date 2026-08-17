from datetime import date
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from apps.core.models import Settings
from apps.exhibitions.models import Exhibition, ExhibitionImage, ExhibitionProgram
from apps.works.models import Artist, Artwork

SEED_DIR = Path(__file__).resolve().parent / "seed_assets"


def _lerp(a, b, t):
    return int(a + (b - a) * t)


def _gradient(size, top, bottom):
    width, height = size
    img = Image.new("RGB", size)
    pixels = img.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        color = (
            _lerp(top[0], bottom[0], t),
            _lerp(top[1], bottom[1], t),
            _lerp(top[2], bottom[2], t),
        )
        for x in range(width):
            pixels[x, y] = color
    return img


def paint(name, size, top, bottom, extras="horizon"):
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    path = SEED_DIR / name
    if path.exists():
        return path
    img = _gradient(size, top, bottom)
    draw = ImageDraw.Draw(img)
    w, h = size
    if extras == "horizon":
        sun = (int(w * 0.72), int(h * 0.28), int(w * 0.08))
        draw.ellipse(
            (sun[0] - sun[2], sun[1] - sun[2], sun[0] + sun[2], sun[1] + sun[2]),
            fill=(196, 112, 72),
        )
        draw.rectangle((0, int(h * 0.62), w, h), fill=(176, 154, 118))
        draw.polygon(
            [(int(w * 0.18), int(h * 0.62)), (int(w * 0.38), int(h * 0.36)), (int(w * 0.58), int(h * 0.62))],
            fill=(154, 132, 98),
        )
        draw.polygon(
            [(int(w * 0.42), int(h * 0.62)), (int(w * 0.55), int(h * 0.44)), (int(w * 0.68), int(h * 0.62))],
            fill=(138, 118, 88),
        )
        # solar boat line
        y = int(h * 0.78)
        draw.arc((int(w * 0.22), y - 18, int(w * 0.78), y + 36), 200, 340, fill=(42, 36, 28), width=4)
    elif extras == "canvas":
        margin = int(min(w, h) * 0.12)
        draw.rectangle((margin, margin, w - margin, h - margin), outline=(42, 36, 28), width=10)
        draw.rectangle(
            (int(w * 0.22), int(h * 0.2), int(w * 0.78), int(h * 0.78)),
            fill=(184, 92, 56),
        )
        draw.ellipse((int(w * 0.38), int(h * 0.28), int(w * 0.72), int(h * 0.62)), fill=(232, 214, 186))
    elif extras == "portrait":
        draw.ellipse((int(w * 0.28), int(h * 0.14), int(w * 0.72), int(h * 0.52)), fill=(92, 72, 54))
        draw.rectangle((int(w * 0.22), int(h * 0.5), int(w * 0.78), int(h * 0.92)), fill=(58, 48, 40))
    elif extras == "nile":
        draw.rectangle((0, int(h * 0.55), w, h), fill=(72, 98, 104))
        draw.polygon(
            [(0, int(h * 0.55)), (int(w * 0.4), int(h * 0.42)), (w, int(h * 0.55))],
            fill=(196, 168, 122),
        )
    elif extras == "interior":
        draw.rectangle((int(w * 0.12), int(h * 0.18), int(w * 0.88), int(h * 0.82)), outline=(42, 36, 28), width=6)
        draw.rectangle((int(w * 0.2), int(h * 0.26), int(w * 0.48), int(h * 0.72)), fill=(176, 88, 54))
        draw.rectangle((int(w * 0.54), int(h * 0.3), int(w * 0.8), int(h * 0.7)), fill=(214, 190, 150))
    img.save(path, format="JPEG", quality=88, optimize=True)
    return path


def jpeg_bytes(path):
    return ContentFile(Path(path).read_bytes(), name=Path(path).name)


class Command(BaseCommand):
    help = "Load Sun Boats settings, editions, program, artists, and works."

    def handle(self, *args, **options):
        hero = paint("hero.jpg", (1920, 1080), (232, 214, 186), (120, 92, 64), "horizon")
        logo = paint("logo.jpg", (600, 600), (244, 239, 230), (214, 196, 164), "canvas")
        e7 = paint("ex7.jpg", (1600, 1060), (236, 220, 190), (132, 96, 62), "horizon")
        e6 = paint("ex6.jpg", (1600, 1060), (224, 200, 164), (88, 72, 54), "interior")
        e5 = paint("ex5.jpg", (1600, 1060), (210, 186, 150), (110, 86, 60), "horizon")
        e4 = paint("ex4.jpg", (1600, 1060), (198, 176, 140), (70, 96, 92), "nile")
        a1 = paint("artist1.jpg", (900, 1100), (214, 198, 176), (92, 74, 56), "portrait")
        a2 = paint("artist2.jpg", (900, 1100), (204, 186, 164), (64, 56, 48), "portrait")
        w1 = paint("work1.jpg", (1200, 1400), (230, 210, 180), (168, 86, 52), "canvas")
        w2 = paint("work2.jpg", (1200, 1400), (210, 196, 170), (72, 98, 104), "nile")
        w3 = paint("work3.jpg", (1200, 1400), (236, 224, 200), (138, 112, 78), "horizon")
        w4 = paint("work4.jpg", (1200, 1400), (220, 188, 150), (92, 64, 48), "interior")
        g1 = paint("gal1.jpg", (1400, 1000), (228, 208, 176), (148, 112, 72), "horizon")
        g2 = paint("gal2.jpg", (1400, 1000), (186, 200, 196), (58, 82, 88), "nile")
        g3 = paint("gal3.jpg", (1400, 1000), (236, 226, 208), (160, 96, 64), "interior")

        settings, _ = Settings.objects.get_or_create(pk=1)
        settings.site_name = "Sun Boats"
        settings.tagline = "International exhibitions in Egypt"
        settings.description = (
            "Sun Boats International Exhibitions — معارض مراكب الشمس — "
            "is a seasonal gathering of artists in Egypt. Painters send a work. "
            "We review it. Selected pieces are shown during the edition week, "
            "alongside visits to Giza, the Grand Egyptian Museum, the Nile, and Minya."
        )
        settings.email = "esmaelbakr28@gmail.com"
        settings.phone = "010 04189135"
        settings.whatsapp = "010 04189135"
        settings.address = "Cairo, Egypt"
        settings.facebook = "https://www.facebook.com/Esmaelbakr28/"
        settings.instagram = "https://www.instagram.com/sun_boats_exhibition/"
        settings.youtube = "https://www.youtube.com/@sunboatsexhibitions4049"
        if not settings.logo:
            settings.logo.save("logo.jpg", jpeg_bytes(logo), save=False)
        if not settings.hero_image:
            settings.hero_image.save("hero.jpg", jpeg_bytes(hero), save=False)
        settings.save()

        editions = [
            {
                "slug": "7th-symposium-2026",
                "title": "7th International Symposium",
                "description": (
                    "The seventh Sun Boats symposium returns to Giza in October 2026. "
                    "Artists work in the presence of the pyramids — not as a backdrop, "
                    "but as the scale against which a painting has to stand. "
                    "This is the next open edition."
                ),
                "start": date(2026, 10, 5),
                "end": date(2026, 10, 12),
                "status": Exhibition.STATUS_UPCOMING,
                "location": "Giza / Pyramids",
                "image": e7,
            },
            {
                "slug": "6th-symposium-egypts-gift-2026",
                "title": "6th Symposium — Egypt’s Gift to the World",
                "description": (
                    "From 1 to 7 May 2026, Sun Boats held its sixth symposium in Giza "
                    "under the title Egypt’s Gift to the World. The week moved between "
                    "the studio, the plateau, the river, and a closing exhibition — "
                    "one edition, not a side programme of tourist events."
                ),
                "start": date(2026, 5, 1),
                "end": date(2026, 5, 7),
                "status": Exhibition.STATUS_PAST,
                "location": "Giza",
                "image": e6,
            },
            {
                "slug": "5th-symposium-2025",
                "title": "5th International Symposium",
                "description": (
                    "October 2025 in Giza. A quieter edition: fewer nights, "
                    "the same open call, the same insistence that a painting "
                    "can meet Egypt without becoming a souvenir."
                ),
                "start": date(2025, 10, 6),
                "end": date(2025, 10, 12),
                "status": Exhibition.STATUS_PAST,
                "location": "Giza",
                "image": e5,
            },
            {
                "slug": "4th-festival-minya-2025",
                "title": "4th Festival — Minya",
                "description": (
                    "9–15 February 2025, the festival travelled south to Minya. "
                    "Workshops, river light, and a closing hang in a city that "
                    "rarely appears on the international exhibition circuit."
                ),
                "start": date(2025, 2, 9),
                "end": date(2025, 2, 15),
                "status": Exhibition.STATUS_PAST,
                "location": "Minya",
                "image": e4,
            },
        ]

        created = {}
        for data in editions:
            obj, was_created = Exhibition.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "description": data["description"],
                    "start_date": data["start"],
                    "end_date": data["end"],
                    "status": data["status"],
                    "location": data["location"],
                },
            )
            obj.title = data["title"]
            obj.description = data["description"]
            obj.start_date = data["start"]
            obj.end_date = data["end"]
            obj.status = data["status"]
            obj.location = data["location"]
            if not obj.image:
                obj.image.save(f"{data['slug']}.jpg", jpeg_bytes(data["image"]), save=False)
            obj.save()
            created[data["slug"]] = obj

        sixth = created["6th-symposium-egypts-gift-2026"]
        program = [
            {
                "title": "Opening workshop",
                "kind": ExhibitionProgram.KIND_WORKSHOP,
                "date": date(2026, 5, 1),
                "place": "Giza studio hall",
                "short_text": "Artists arrive, stretch, and begin in shared light.",
            },
            {
                "title": "Pyramids visit",
                "kind": ExhibitionProgram.KIND_VISIT,
                "date": date(2026, 5, 3),
                "place": "Giza Plateau",
                "short_text": "A working day on the plateau — looking, drawing, not posing.",
            },
            {
                "title": "Nile crossing",
                "kind": ExhibitionProgram.KIND_VISIT,
                "date": date(2026, 5, 5),
                "place": "The Nile",
                "short_text": "Afternoon on the river between Giza and Cairo.",
            },
            {
                "title": "Closing show",
                "kind": ExhibitionProgram.KIND_SHOW,
                "date": date(2026, 5, 7),
                "place": "Edition gallery, Giza",
                "short_text": "The week hangs as one exhibition and is documented.",
            },
        ]
        for item in program:
            ExhibitionProgram.objects.get_or_create(
                exhibition=sixth,
                title=item["title"],
                defaults=item,
            )

        if not sixth.gallery_images.exists():
            for path, caption in (
                (g1, "Plateau light, 6th symposium"),
                (g2, "Nile afternoon"),
                (g3, "Closing hang"),
            ):
                img = ExhibitionImage(exhibition=sixth, caption=caption)
                img.image.save(Path(path).name, jpeg_bytes(path), save=True)

        nour, _ = Artist.objects.get_or_create(
            name="Nour El-Sayed",
            defaults={
                "country": "Egypt",
                "bio": "Painter based in Cairo. Works with limestone dust, oil, and large quiet fields of colour.",
            },
        )
        if not nour.image:
            nour.image.save("nour.jpg", jpeg_bytes(a1), save=False)
            nour.save()
        elena, _ = Artist.objects.get_or_create(
            name="Elena Vargas",
            defaults={
                "country": "Spain",
                "bio": "Madrid-born painter. Joined Sun Boats to work at the scale of Egyptian light.",
            },
        )
        if not elena.image:
            elena.image.save("elena.jpg", jpeg_bytes(a2), save=False)
            elena.save()

        seventh = created["7th-symposium-2026"]
        works = [
            ("Limestone Hour", nour, seventh, "2026", "Oil on linen", w1, "A slow field of sand and wall."),
            ("Gift of the River", elena, seventh, "2026", "Acrylic on canvas", w2, "Horizontal water, held still."),
            ("After the Plateau", nour, seventh, "2026", "Mixed media", w3, "What remains when the monument steps back."),
            ("Edition Light", elena, seventh, "2026", "Oil on canvas", w4, "Studio colour under a Giza afternoon."),
            ("Minya Evening", nour, sixth, "2025", "Oil on linen", w3, "A darker field from an earlier week."),
            ("River Gift", elena, sixth, "2026", "Acrylic on canvas", w2, "The May week, seen from the water."),
        ]
        for title, artist, exhibition, year, medium, path, desc in works:
            art, _made = Artwork.objects.get_or_create(
                slug=title.lower().replace(" ", "-"),
                defaults={
                    "title": title,
                    "artist": artist,
                    "exhibition": exhibition,
                    "year": year,
                    "medium": medium,
                    "description": desc,
                },
            )
            if not art.image:
                art.image.save(f"{art.slug}.jpg", jpeg_bytes(path), save=False)
                art.save()

        self.stdout.write(self.style.SUCCESS("Sun Boats seed complete."))
