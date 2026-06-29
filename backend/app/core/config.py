from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Hotel PMS"
    debug: bool = True


settings = Settings()
