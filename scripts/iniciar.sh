#!/usr/bin/env bash
# Levanta Ñangarekó IA completo en macOS / Linux / WSL.
#   ./scripts/iniciar.sh                    normal, en http://localhost
#   ./scripts/iniciar.sh --demo             tormenta simulada + datos de ejemplo
#   ./scripts/iniciar.sh --demo --publico   además, link HTTPS público para celulares
#   ./scripts/iniciar.sh --detener          apaga todo (los datos se conservan)
set -euo pipefail
cd "$(dirname "$0")/.."

DEMO=0; PUBLICO=0
for arg in "$@"; do
  case "$arg" in
    --demo) DEMO=1 ;;
    --publico) PUBLICO=1 ;;
    --detener) docker compose --profile publico stop; echo "Ñangarekó IA detenido."; exit 0 ;;
    *) echo "Opción desconocida: $arg"; exit 1 ;;
  esac
done

command -v docker >/dev/null || { echo "Instalá Docker: https://docs.docker.com/get-docker/"; exit 1; }
docker info >/dev/null 2>&1 || { echo "Docker no está corriendo: inicialo y reintentá."; exit 1; }

[ -f .env ] || { cp .env.example .env; echo "Se creó .env: completá ANTHROPIC_API_KEY para activar la IA (opcional)."; }
# El modo se guarda en .env (Compose lo lee siempre): así un "docker compose up" posterior no lo apaga sin querer.
MODO=""; [ "$DEMO" = 1 ] && MODO=tormenta
if grep -q '^CLIMA_DEMO=' .env; then
  sed -i.bak "s/^CLIMA_DEMO=.*/CLIMA_DEMO=$MODO/" .env && rm -f .env.bak
else
  echo "CLIMA_DEMO=$MODO" >> .env
fi
unset CLIMA_DEMO  # que mande .env, no una variable vieja de la sesión

PERFIL=()
[ "$PUBLICO" = 1 ] && PERFIL=(--profile publico)
docker compose "${PERFIL[@]}" up -d --build

echo "Esperando a que la API responda..."
for _ in $(seq 1 60); do curl -sf http://localhost/api/salud >/dev/null && break; sleep 2; done
curl -sf http://localhost/api/salud >/dev/null || { echo "La API no respondió: docker compose logs api"; exit 1; }

if [ "$DEMO" = 1 ]; then
  docker compose exec -T db psql -q -U naangareko -f /demo/demo.sql
  echo "Datos de ejemplo cargados (las Zonas Rojas duran ~2 h)."
fi

echo
echo "Ñangarekó IA está listo:"
echo "  App en esta computadora:  http://localhost"
echo "  API (Swagger):            http://localhost:8000/docs"
for ip in $(hostname -I 2>/dev/null || ipconfig getifaddr en0 2>/dev/null || true); do
  echo "  Otros equipos de tu red:  http://$ip  (sin cámara/GPS: requieren HTTPS)"
done

if [ "$PUBLICO" = 1 ]; then
  # Se pregunta al propio túnel (no a los logs, que guardan URLs viejas de arranques anteriores).
  URL=""
  for _ in $(seq 1 30); do
    URL=$(curl -sf http://127.0.0.1:2000/quicktunnel | grep -o '[a-z0-9-]*\.trycloudflare\.com' || true)
    [ -n "$URL" ] && break; sleep 2
  done
  echo "  Link público (celulares): ${URL:+https://}${URL:-todavía arrancando, ver: docker compose logs tunel}"
fi
