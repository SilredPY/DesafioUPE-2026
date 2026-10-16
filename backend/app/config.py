from pydantic_settings import BaseSettings, SettingsConfigDict

from app.modules.clima.domain import Temporada


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://naangareko:naangareko@localhost:5432/naangareko"
    # ANTHROPIC_API_KEY lo lee directamente el SDK de Anthropic.
    anthropic_model: str = "claude-opus-5-5"
    # shortcut: temporada ENSO fijada a mano; integrar índice ONI de NOAA cuando haga falta automatizarlo.
    temporada_enso: Temporada = Temporada.NEUTRAL
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:4173"]
    max_foto_bytes: int = 5 * 1024 * 1024


settings = Settings()
