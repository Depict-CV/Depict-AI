import os

import yaml
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_URL = os.getenv("API_URL")
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # OAuth2 Google Configuration
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    
    # OAuth2 Microsoft Configuration
    MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID", "")
    MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET", "")
    MICROSOFT_REDIRECT_URI = os.getenv("MICROSOFT_REDIRECT_URI", "http://localhost:8000/auth/microsoft/callback")
    
    # OAuth2 GitHub Configuration
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
    GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback")
    
    # Frontend URL for OAuth redirects
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    base_dir = os.path.dirname(__file__)
    yaml_path = os.path.join(base_dir, "src", "config.yaml")
    with open(yaml_path) as f:
        yaml_config = yaml.safe_load(f)

    annotation = yaml_config.get("annotation", {})


config = Config()

# Export individual config values for easier importing
API_URL = config.API_URL
SENTRY_DSN = config.SENTRY_DSN
JWT_SECRET_KEY = config.JWT_SECRET_KEY
JWT_ALGORITHM = config.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES
GOOGLE_CLIENT_ID = config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = config.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = config.GOOGLE_REDIRECT_URI
MICROSOFT_CLIENT_ID = config.MICROSOFT_CLIENT_ID
MICROSOFT_CLIENT_SECRET = config.MICROSOFT_CLIENT_SECRET
MICROSOFT_REDIRECT_URI = config.MICROSOFT_REDIRECT_URI
GITHUB_CLIENT_ID = config.GITHUB_CLIENT_ID
GITHUB_CLIENT_SECRET = config.GITHUB_CLIENT_SECRET
GITHUB_REDIRECT_URI = config.GITHUB_REDIRECT_URI
FRONTEND_URL = config.FRONTEND_URL
