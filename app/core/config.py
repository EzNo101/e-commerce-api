from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database

    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAY: int = 7
    ALGORITHM: str = "HS256"

    # External services
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str

    # Cache
    REDIS_URL: str
    CACHE_TTL: int

    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
