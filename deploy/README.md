# Deploy Sun Boats

App path: `/var/www/sunboats`  
Service: `sunboats` (gunicorn)  
Web: nginx → `127.0.0.1:8000`

Do not store passwords in this file. They live only in `/var/www/sunboats/.env` (mode 600).

## After a code pull

```bash
cd /var/www/sunboats
sudo -u sunboats git pull
sudo -u sunboats .venv/bin/pip install -r requ.txt
sudo -u sunboats env DJANGO_SETTINGS_MODULE=config.settings.prod .venv/bin/python manage.py migrate
sudo -u sunboats env DJANGO_SETTINGS_MODULE=config.settings.prod .venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart sunboats
sudo systemctl reload nginx
```

Seed only if the database is empty:

```bash
sudo -u sunboats env DJANGO_SETTINGS_MODULE=config.settings.prod .venv/bin/python manage.py seed_sunboats
```

## Where to edit exhibitions

Sign in at `https://sunboats.online/admin/`

- Next edition: **المعارض**
- Week programme rows: inside that exhibition
- Incoming paintings: **طلبات العرض** (filter by status, accept or reject)

## DNS

The public site is the domain only. Do not add the VPS IP to `ALLOWED_HOSTS`.

```
sunboats.online      A   159.223.182.218
www.sunboats.online  A   159.223.182.218
```

Then:

```bash
certbot --nginx -d sunboats.online -d www.sunboats.online --redirect
```
