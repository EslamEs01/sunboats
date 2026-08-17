# Sun Boats International Exhibitions

Website for **Sun Boats** (معارض مراكب الشمس) — seasonal international art exhibitions in Egypt, founded by Ismail Bakr (Esmael Bakr).

Public pages: Home, Exhibitions, Submit your work, About. Admin is at `/admin/`.

## Run locally

You need Python 3.12+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requ.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_sunboats
python manage.py runserver
```

Open http://127.0.0.1:8000/

If Postgres is not configured, the site uses a local SQLite file automatically.

To rebuild CSS after editing `static/src/input.css`:

```bash
npm install
npm run build:css
```

The compiled file `static/css/app.css` is already in the repo, so you do not need Node just to run the site.

## Add the next exhibition

1. Sign in at `/admin/`
2. Open **المعارض** → **المعارض**
3. Add an exhibition: title, dates, city, image, status (`قادم` for upcoming)
4. In the same page, add **برنامج المعرض** rows for that week (workshop, pyramids visit, Nile, closing show)
5. Add gallery photographs in the images section

## Approve a painting

1. An artist sends work on `/submit/`
2. Open **المعارض** → **طلبات العرض**
3. Filter by **الحالة** (`قيد المراجعة`)
4. Open the request, look at the image
5. In the list, change الحالة to **مقبول** or **مرفوض**, or use the actions **قبول الطلبات المحددة** / **رفض الطلبات المحددة**

## Production notes

See `deploy/README.md`. Never put passwords in this file.
