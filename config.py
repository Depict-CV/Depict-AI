import os

import yaml
from dotenv import load_dotenv

load_dotenv()


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    API_URL = os.getenv("API_URL")
    SENTRY_DSN = os.getenv("SENTRY_DSN")

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # Frontend URL for OAuth redirects
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Clerk Configuration
    CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "")
    CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "")
    CLERK_ISSUER = os.getenv("CLERK_ISSUER", "")

    # Feature toggles
    AUTH_ENABLED = env_bool("AUTH_ENABLED", True)
    SENTRY_ENABLED = env_bool("SENTRY_ENABLED", True)

    base_dir = os.path.dirname(__file__)
    yaml_path = os.path.join(base_dir, "src", "config.yaml")
    with open(yaml_path) as f:
        yaml_config = yaml.safe_load(f)

    annotation = yaml_config.get("annotation", {})


config = Config()
