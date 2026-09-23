# quinio.tech streaming stack

Self-hosted family stack on a Contabo VPS (Ubuntu 24.04, TZ Europe/Berlin). Viren070 docker-compose template.

## Layout
- Root: /opt/docker (run ALL compose commands from here, never from apps/*)
- Apps: apps/<name>/compose.yaml, each listed in root compose.yaml `include:`
- Data: data/<name>/ (not in git). Dispatcharr data: apps/dispatcharr/data
- Enabled apps are set via COMPOSE_PROFILES in root .env

## Conventions (Viren070 template)
- Use `expose:` not `ports:`; no `networks:` section in app compose files
- Secrets and hostnames go in root .env, never in compose files
- Traefik labels for Dispatcharr live in apps/gluetun/compose.yaml (network_mode: service:gluetun)
- Admin UIs go behind the Authelia middleware; Jellyfin and dispatcharr-xc are intentionally public

## Rules
- Never print, cat, or echo .env values or apps/authelia/config/users.yml
- Ask before touching Traefik, Authelia, or Gluetun: a mistake there takes down everything
- Explain the change and show the diff before any `docker compose up -d` or restart
- After config changes: git add, commit with a clear message; ask before pushing
- Backups: restic -> B2 nightly via /usr/local/bin/backup-stack.sh (root cron, 11:00 Berlin)
