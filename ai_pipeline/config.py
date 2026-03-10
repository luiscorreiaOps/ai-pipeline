import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from .providers import KNOWN_KEYS

load_dotenv()

class Config(BaseModel):
    ai_api_key: str = Field(default_factory=lambda: os.getenv("AI_API_KEY", ""))
    ai_provider_key: str = Field(default_factory=lambda: os.getenv("AI_PROVIDER_KEY", ""))

    def is_valid(self) -> bool:
        """Returns true if an API key is present."""
        return bool(self.ai_api_key)

    def scan_environment(self):
        """Scans for known AI provider keys in the environment."""
        found = {}
        for key in KNOWN_KEYS:
            val = os.getenv(key)
            if val:
                found[key] = val
        return found

config = Config()
