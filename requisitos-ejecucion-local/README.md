# Requerimientos para la ejecución local de este proyecto

Qué tiene que tener tu computadora para correr **Ñangarekó IA**. Esta lista **crece con el proyecto**: cada vez que una mejora necesite algo nuevo, se agrega acá y en el verificador. Mirá el [historial](#historial-de-cambios) después de cada `git pull`.

## ✅ Verificación automática (Windows)

**Doble clic en `verificar.cmd`** (esta misma carpeta). También desde una terminal:

```powershell
.\requisitos-ejecucion-local\verificar.ps1              # revisa y pregunta antes de instalar cada cosa
.\requisitos-ejecucion-local\verificar.ps1 -SoloRevisar # solo muestra el estado
```

El verificador revisa cada requisito y muestra `[OK]`, `[FALTA]` (obligatorio) o `[--]` (opcional). Si algo falta y se puede instalar solo, pregunta **"¿Instalarlo ahora? (s/n)"** y lo instala con `winget`, el instalador que ya viene con Windows 10/11. Puede aparecer la ventana de permisos de Windows (UAC): aceptala.

Cuando todo da OK: doble clic en `scripts\iniciar.cmd`, o `scripts\demo-publico.cmd` para presentar.

## 📋 Obligatorios

| Requisito | Para qué | Cómo conseguirlo |
|---|---|---|
| **Windows 10 (2004+) u 11, 64 bits** | Docker Desktop no corre en versiones anteriores | Windows Update |
| **WSL 2** | Docker Desktop lo usa para los contenedores Linux | El verificador lo instala (`wsl --install`). Pide **reiniciar** |
| **Git** | Bajar la repo y traer los cambios del equipo (`git pull`) | El verificador lo instala · [git-scm.com](https://git-scm.com/download/win) |
| **Docker Desktop** | Corre la base de datos, la API, la web y el link público. Por eso **no** hace falta instalar Python, Node ni PostgreSQL | El verificador lo instala · [docker.com](https://www.docker.com/products/docker-desktop/). Abrilo una vez y aceptá los términos |
| **Docker Compose v2** | Los scripts levantan todo junto con `docker compose` | Viene con Docker Desktop |
| **Docker Desktop abierto** | Los scripts de iniciar y detener lo necesitan corriendo | El verificador lo abre y espera a que arranque |
| **Puertos 80, 8000, 5432 y 2000 libres** | 80: la app · 8000: la API · 5432: la base · 2000: el link público | Cerrá lo que los use (IIS, XAMPP, Apache, Skype, otro PostgreSQL). El verificador dice qué programa es |
| **6 GB libres en disco** | Imágenes de Docker y base de datos (~4 GB) | Liberar espacio en `C:` |
| **Internet** | La primera descarga, el pronóstico (Open-Meteo) y el link público (Cloudflare) | — |

## 🧰 Opcionales

| Requisito | Para qué | Cómo conseguirlo |
|---|---|---|
| **8 GB de RAM** | Con menos funciona, pero lento | — |
| **Node.js 24+** | Programar el frontend con recarga en caliente (`npm run dev`) | El verificador lo instala · [nodejs.org](https://nodejs.org/) |
| **Python 3.12+** | Correr los tests del backend sin Docker | El verificador lo instala · [python.org](https://www.python.org/downloads/) |
| **Clave de Anthropic** (`ANTHROPIC_API_KEY` en `.env`) | Mensajes en lenguaje del barrio y clasificación de fotos. Sin clave todo funciona con el texto técnico | La pide quien presenta. **Nunca la subas a git** ni la pegues en el chat del equipo |
| **`ADMIN_TOKEN`** en `.env` | Publicar avisos y agregar instituciones en 🎓 Campus | `python -c "import secrets; print(secrets.token_urlsafe(24))"` |
| **Un celular** | Probar cámara, GPS e instalación de la app (requieren el link HTTPS de `demo-publico.cmd`) | — |

## 🍎 macOS / 🐧 Linux

No hay verificador automático: instalá a mano **Git** y **Docker Desktop** (o Docker Engine + el plugin Compose v2 en Linux), con los mismos puertos libres, y usá `./scripts/iniciar.sh`.

## 🔧 Para quien agregue requisitos

Si tu cambio necesita algo nuevo en la compu (otro programa, otro puerto, una variable en `.env`):

1. Agregá un bloque en la **LISTA DE REQUISITOS** de `verificar.ps1`, con `Nombre`, `Para`, `Obligatorio`, `Link`, `Probar` y, si se puede instalar con winget, `Instalar`.
2. Agregá la fila en la tabla de arriba.
3. Anotalo en el historial de abajo, con la fecha.
4. Si cambia cómo se arranca o se apaga el proyecto, actualizá `scripts/iniciar.ps1`, `scripts/iniciar.sh` y los `.cmd`.

## Historial de cambios

| Fecha | Cambio |
|---|---|
| 2026-10-16 | Primera versión de la lista y del verificador. |
