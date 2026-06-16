from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    database_url: str = "sqlite:///./ncs_dash.db"
    slack_webhook_url: str = ""
    secret_key: str = "changeme"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    scraper_interval_hours: int = 4
    ncs_base_url: str = "https://www.nationalchampionshipsports.com"
    monitored_divisions: str = "10U,12U"
    monitored_cities: str = "Austin,Cedar Park,Round Rock,Georgetown,Pflugerville,Leander,Kyle,Buda"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def divisions_list(self) -> List[str]:
        return [d.strip() for d in self.monitored_divisions.split(",")]

    @property
    def cities_list(self) -> List[str]:
        return [c.strip() for c in self.monitored_cities.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
