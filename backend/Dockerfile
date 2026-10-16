# 1) Compila el motor C++ (pybind11) a un wheel.
FROM python:3.12-slim AS nativo
RUN apt-get update && apt-get install -y --no-install-recommends g++ && rm -rf /var/lib/apt/lists/*
COPY nativo /src/nativo
RUN pip wheel --no-cache-dir -w /wheels /src/nativo

# 2) Imagen de la API.
FROM python:3.12-slim AS app
WORKDIR /app
COPY --from=nativo /wheels /wheels
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir /wheels/*.whl . && rm -rf /wheels && useradd --system --no-create-home app

# 3) Tests dentro de la imagen real (incluye la paridad C++ vs Python): docker build --target pruebas
FROM app AS pruebas
RUN pip install --no-cache-dir pytest
COPY tests ./tests
COPY nativo/bench.py ./nativo/bench.py
CMD ["pytest", "-q"]

# 4) Imagen final (por defecto).
FROM app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/salud')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
