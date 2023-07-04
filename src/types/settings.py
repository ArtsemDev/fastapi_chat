from pydantic import BaseSettings, SecretStr, PositiveInt, Field, PostgresDsn


class Settings(BaseSettings):
    SECRET_KEY: SecretStr
    EXPIRE_JWT: PositiveInt
    ALGORITHM: str = Field(default='HS256')
    TOKEN_TYPE: str = Field(default='Bearer')
    DATABASE_URL: PostgresDsn
