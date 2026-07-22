#!/usr/bin/env bash
# Oracle Cloud Always Free (Ampere A1, Ubuntu 24.04 ARM64) — backend bootstrap.
# Run as the `ubuntu` user:  bash setup.sh
set -euo pipefail

REPO="https://github.com/macklinkim/sector_analyzer.git"
DEST="/opt/economi_analyzer"

echo "== System packages =="
sudo apt-get update
# Ubuntu 24.04 ships Python 3.12. gcc/build tools for any source wheels.
sudo apt-get install -y python3.12 python3.12-venv python3-pip git build-essential curl

echo "== Clone / update repo =="
if [ ! -d "$DEST/.git" ]; then
  sudo mkdir -p "$DEST"
  sudo chown "$USER":"$USER" "$DEST"
  git clone "$REPO" "$DEST"
else
  git -C "$DEST" pull --ff-only
fi

echo "== Python venv + deps =="
python3.12 -m venv "$DEST/.venv"
"$DEST/.venv/bin/pip" install --upgrade pip
"$DEST/.venv/bin/pip" install -e "$DEST/backend"

echo "== .env =="
if [ ! -f "$DEST/backend/.env" ]; then
  cp "$DEST/backend/deploy/.env.example" "$DEST/backend/.env"
  echo "!! Edit $DEST/backend/.env with real keys before starting the service."
fi

echo "== systemd service =="
sudo cp "$DEST/backend/deploy/economi-backend.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable economi-backend
echo "Start with: sudo systemctl start economi-backend  (after editing .env)"

echo "== Firewall (Ubuntu iptables — Oracle images block by default) =="
# Open 80/443 for Caddy TLS + 8000 optional. Also open in Oracle console Security List!
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save || (sudo apt-get install -y iptables-persistent && sudo netfilter-persistent save)

echo "== Caddy (auto HTTPS reverse proxy) =="
sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt-get update && sudo apt-get install -y caddy
echo "Edit /etc/caddy/Caddyfile (copy from backend/deploy/Caddyfile, set your domain), then: sudo systemctl restart caddy"

echo "== Done. Next steps in deploy/README.md =="
