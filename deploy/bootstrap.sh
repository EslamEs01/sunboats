#!/bin/bash
# Run as root on the VPS after the app files are in /var/www/sunboats.
# Generates secrets on the machine. Does not print them.

set -euo pipefail
APP=/var/www/sunboats
export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y nginx postgresql python3-venv python3-pip \
  python3-certbot-nginx certbot git build-essential libpq-dev ufw rsync
systemctl enable --now postgresql

id sunboats >/dev/null 2>&1 || useradd --system --create-home --shell /bin/bash sunboats
mkdir -p "$APP/media" "$APP/staticfiles"
chown -R sunboats:sunboats "$APP"

if [ ! -f "$APP/.env" ]; then
  SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')
  PGPASS=$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')
  cat > "$APP/.env" <<EOF
SECRET_KEY=$SECRET
DEBUG=0
ALLOWED_HOSTS=.sunboats.online,159.223.182.218,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://sunboats.online,https://www.sunboats.online,http://159.223.182.218
POSTGRES_DB=sunboats
POSTGRES_USER=sunboats
POSTGRES_PASSWORD=$PGPASS
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
DJANGO_SETTINGS_MODULE=config.settings.prod
EOF
  chmod 600 "$APP/.env"
  chown sunboats:sunboats "$APP/.env"
  sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='sunboats'" | grep -q 1 \
    || sudo -u postgres psql -c "CREATE USER sunboats WITH PASSWORD '${PGPASS}';"
  sudo -u postgres psql -c "ALTER USER sunboats WITH PASSWORD '${PGPASS}';"
  sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='sunboats'" | grep -q 1 \
    || sudo -u postgres createdb -O sunboats sunboats
  sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sunboats TO sunboats;"
fi

sudo -u sunboats python3 -m venv "$APP/.venv"
sudo -u sunboats "$APP/.venv/bin/pip" install --upgrade pip
sudo -u sunboats "$APP/.venv/bin/pip" install -r "$APP/requ.txt"

sudo -u sunboats env DJANGO_SETTINGS_MODULE=config.settings.prod \
  "$APP/.venv/bin/python" "$APP/manage.py" migrate --noinput
sudo -u sunboats env DJANGO_SETTINGS_MODULE=config.settings.prod \
  "$APP/.venv/bin/python" "$APP/manage.py" collectstatic --noinput

COUNT=$(sudo -u sunboats env DJANGO_SETTINGS_MODULE=config.settings.prod \
  "$APP/.venv/bin/python" "$APP/manage.py" shell -c 'from apps.exhibitions.models import Exhibition; print(Exhibition.objects.count())')
if [ "$COUNT" = "0" ]; then
  sudo -u sunboats env DJANGO_SETTINGS_MODULE=config.settings.prod \
    "$APP/.venv/bin/python" "$APP/manage.py" seed_sunboats
fi

if ! sudo -u sunboats env DJANGO_SETTINGS_MODULE=config.settings.prod \
  "$APP/.venv/bin/python" "$APP/manage.py" shell -c 'from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(is_superuser=True).exists())' | grep -q True; then
  ADMIN_PASS=$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')
  sudo -u sunboats env DJANGO_SETTINGS_MODULE=config.settings.prod \
    "$APP/.venv/bin/python" "$APP/manage.py" shell -c \
    "from django.contrib.auth import get_user_model; u=get_user_model().objects.create_superuser('ismail','esmaelbakr28@gmail.com','$ADMIN_PASS'); print('created', u.username)"
  umask 077
  printf 'username: ismail\npassword: %s\n' "$ADMIN_PASS" > /root/sunboats-admin.txt
fi

cp "$APP/deploy/sunboats.service" /etc/systemd/system/sunboats.service
cp "$APP/deploy/nginx.conf" /etc/nginx/sites-available/sunboats
ln -sfn /etc/nginx/sites-available/sunboats /etc/nginx/sites-enabled/sunboats
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl daemon-reload
systemctl enable --now sunboats
systemctl restart sunboats
systemctl restart nginx

ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

certbot --nginx -d sunboats.online -d www.sunboats.online \
  --non-interactive --agree-tos -m esmaelbakr28@gmail.com --redirect || true

echo "bootstrap finished"
