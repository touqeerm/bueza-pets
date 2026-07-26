#!/usr/bin/env bash
# One-time SSL bootstrap for app.bueza.in / api.bueza.in / staging.app.bueza.in
# / staging.api.bueza.in. Safe to re-run (certbot no-ops if the cert is
# already valid; nginx reload is idempotent).
#
# Run this AFTER DNS for all four hostnames resolves to this server —
# certbot's webroot validation will fail otherwise. See the DNS section
# of the README for exact records.
#
# Sequence, and why: the full nginx/z-bueza-pets.conf references certs
# that don't exist yet, so deploying it first would fail `nginx -t` and
# refuse to reload (a safe failure, but it means the site can't go live
# that way). Instead: deploy an HTTP-only version first (just enough for
# certbot's ACME challenge to be served), obtain the real cert, then swap
# in the full config with the cert paths now valid.
#
# Filename note: prefixed "z-" so it sorts alphabetically AFTER the
# existing default.conf and n8n.conf in conf.d/. nginx's include picks a
# default_server for each port from whichever file loads first when none
# is explicitly marked — without the prefix this file would silently
# become the new default for any request with no matching Host header,
# changing pre-existing behavior we have no reason to touch.
set -euo pipefail

NGINX_CONTAINER="odoo16-nginx"
CONF_NAME="z-bueza-pets.conf"
REPO_CONF="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/nginx/z-bueza-pets.conf"
DOMAINS=(app.bueza.in api.bueza.in staging.app.bueza.in staging.api.bueza.in)
CERT_NAME="bueza-pets"
WEBROOT="/opt/odoo/webroot"

echo "==> Stage 1: deploying HTTP-only config (for ACME challenge)..."
TMP_CONF=$(mktemp)
cat > "$TMP_CONF" <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAINS[*]};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 "bueza-pets: awaiting SSL setup\n";
        add_header Content-Type text/plain;
    }
}
EOF

docker cp "$TMP_CONF" "$NGINX_CONTAINER:/etc/nginx/conf.d/$CONF_NAME"
rm -f "$TMP_CONF"
docker exec "$NGINX_CONTAINER" nginx -t
docker exec "$NGINX_CONTAINER" nginx -s reload
echo "==> HTTP-only config live. Verifying each domain resolves here before requesting a cert..."

for domain in "${DOMAINS[@]}"; do
  code=$(curl -s -o /dev/null -m 10 -w "%{http_code}" "http://$domain/" 2>/dev/null); code="${code:-000}"
  echo "    $domain -> HTTP $code"
  if [ "$code" != "200" ]; then
    echo "==> $domain did not respond as expected. Check DNS before continuing (see README)." >&2
    exit 1
  fi
done

echo "==> Stage 2: requesting certificate for: ${DOMAINS[*]}"
DOMAIN_ARGS=()
for d in "${DOMAINS[@]}"; do DOMAIN_ARGS+=(-d "$d"); done

certbot certonly --webroot -w "$WEBROOT" \
  --cert-name "$CERT_NAME" \
  "${DOMAIN_ARGS[@]}" \
  --non-interactive --agree-tos -m "${CERTBOT_EMAIL:?Set CERTBOT_EMAIL=you@example.com}"

echo "==> Stage 3: deploying full HTTPS config..."
docker cp "$REPO_CONF" "$NGINX_CONTAINER:/etc/nginx/conf.d/$CONF_NAME"
docker exec "$NGINX_CONTAINER" nginx -t
docker exec "$NGINX_CONTAINER" nginx -s reload

echo "==> Done. Verifying HTTPS..."
for domain in "${DOMAINS[@]}"; do
  code=$(curl -s -o /dev/null -m 10 -w "%{http_code}" "https://$domain/" 2>/dev/null); code="${code:-000}"
  echo "    https://$domain -> HTTP $code"
done
