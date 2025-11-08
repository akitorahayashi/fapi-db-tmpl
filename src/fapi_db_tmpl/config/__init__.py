from .api_settings import ApiSettings
from .db_settings import DBSettings

api_settings = ApiSettings()
db_settings = DBSettings()

__all__ = ["api_settings", "db_settings"]
