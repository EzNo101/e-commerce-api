from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # External services
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    
    # Cache
    REDIS_URL: str
    CACHE_TTL: int

    DEBUG = True
    
    class Config:
        env_file = ".env"

settings = Settings()