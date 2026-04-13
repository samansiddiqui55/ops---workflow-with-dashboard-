from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class Settings(BaseSettings):
    # MongoDB - use env vars directly
    mongo_url: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name: str = os.environ.get("DB_NAME", "opsflow_db")
    
    # Email - IMAP/SMTP settings
    email_imap_server: str = os.environ.get("EMAIL_IMAP_SERVER", "imap.gmail.com")
    email_imap_port: int = int(os.environ.get("EMAIL_IMAP_PORT", "993"))
    email_smtp_server: str = os.environ.get("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    email_smtp_port: int = int(os.environ.get("EMAIL_SMTP_PORT", "587"))
    email_username: str = os.environ.get("EMAIL_USERNAME", "")
    email_password: str = os.environ.get("EMAIL_PASSWORD", "")
    
    # Email filtering - IMPORTANT: test email for samansiddiqui903@gmail.com
    allowed_test_emails: str = os.environ.get("ALLOWED_TEST_EMAILS", "samansiddiqui903@gmail.com")
    brand_domains: str = os.environ.get("BRAND_DOMAINS", "")
    
    # Jira - NO hardcoded fallback for project key
    jira_base_url: str = os.environ.get("JIRA_BASE_URL", "")
    jira_email: str = os.environ.get("JIRA_EMAIL", "")
    jira_api_token: str = os.environ.get("JIRA_API_TOKEN", "")
    jira_webhook_secret: str = os.environ.get("JIRA_WEBHOOK_SECRET", "")
    jira_project_key: str = os.environ.get("JIRA_PROJECT_KEY", "")
    
    # Slack
    slack_bot_token: str = os.environ.get("SLACK_BOT_TOKEN", "")
    slack_signing_secret: str = os.environ.get("SLACK_SIGNING_SECRET", "")
    slack_bug_channel: str = os.environ.get("SLACK_BUG_CHANNEL", "bug-reporting")
    
    # AI
    emergent_llm_key: str = os.environ.get("EMERGENT_LLM_KEY", "")
    
    # CORS
    cors_origins: str = os.environ.get("CORS_ORIGINS", "*")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
