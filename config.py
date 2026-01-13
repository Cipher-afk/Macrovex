from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    TOKEN: str
    API_KEY: str
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str
    model_config = SettingsConfigDict(env_file="./.env", extra="ignore")


settings = Config()
