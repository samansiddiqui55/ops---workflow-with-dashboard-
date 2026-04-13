# from fastapi import FastAPI, APIRouter
# from fastapi.middleware.cors import CORSMiddleware
# from motor.motor_asyncio import AsyncIOMotorClient
# from dotenv import load_dotenv
# from pathlib import Path
# import os
# import logging

# from config import get_settings
# from routes import webhooks, config_routes, mapping_routes
# from jobs.email_poller import email_poller
# from routes.demo import router as demo_router

# app.include_router(demo_router, prefix="/demo")

# ROOT_DIR = Path(__file__).parent
# load_dotenv(ROOT_DIR / '.env')

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# app = FastAPI(
#     title="OpsFlow - Logistics Issue Automation",
#     description="Automated issue tracking system integrating Email, Slack, and Jira",
#     version="1.0.0"
# )

# api_router = APIRouter(prefix="/api")

# settings = get_settings()
# mongo_client = AsyncIOMotorClient(settings.mongo_url)
# db = mongo_client[settings.db_name]

# app.add_middleware(
#     CORSMiddleware,
#     allow_credentials=True,
#     allow_origins=settings.cors_origins.split(','),
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @api_router.get("/")
# async def root():
#     return {
#         "service": "OpsFlow",
#         "status": "running",
#         "version": "1.0.0",
#         "features": [
#             "Email → Jira workflow",
#             "Jira → Email auto-response",
#             "Slack → Jira workflow",
#             "Jira → Slack thread reply",
#             "AI-powered categorization"
#         ]
#     }

# @api_router.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "database": "connected",
#         "email": "configured" if settings.email_username else "not configured",
#         "jira": "configured" if settings.jira_api_token else "not configured",
#         "slack": "configured" if settings.slack_bot_token else "not configured"
#     }

# @api_router.post("/test/email-poll")
# async def trigger_email_poll():
#     """Manually trigger email polling (for testing)."""
#     await email_poller.process_emails()
#     return {"status": "Email polling triggered"}

# api_router.include_router(webhooks.router)
# api_router.include_router(config_routes.router)
# api_router.include_router(mapping_routes.router)

# app.include_router(api_router)

# @app.on_event("startup")
# async def startup_event():
#     """Initialize services on startup."""
#     logger.info("=== OpsFlow Starting ===")
#     logger.info(f"Database: {settings.db_name}")
#     logger.info(f"Email configured: {bool(settings.email_username)}")
#     logger.info(f"Jira configured: {bool(settings.jira_api_token)}")
#     logger.info(f"Slack configured: {bool(settings.slack_bot_token)}")
    
#     email_poller.start()
#     logger.info("Email poller started")
    
#     try:
#         await db.command("ping")
#         logger.info("MongoDB connection successful")
#     except Exception as e:
#         logger.error(f"MongoDB connection failed: {str(e)}")
    
#     logger.info("=== OpsFlow Ready ===")

# @app.on_event("shutdown")
# async def shutdown_event():
#     """Cleanup on shutdown."""
#     logger.info("Shutting down OpsFlow...")
#     email_poller.stop()
#     mongo_client.close()
#     logger.info("OpsFlow shut down complete")
# from fastapi import FastAPI, APIRouter
# from fastapi.middleware.cors import CORSMiddleware
# from motor.motor_asyncio import AsyncIOMotorClient
# from dotenv import load_dotenv
# from pathlib import Path
# import os
# import logging

# from config import get_settings
# from routes import webhooks, config_routes, mapping_routes
# from jobs.email_poller import email_poller
# from routes.demo import router as demo_router
# from routes import webhooks, config_routes, mapping_routes, tickets

# ROOT_DIR = Path(__file__).parent
# load_dotenv(ROOT_DIR / '.env')

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# app = FastAPI(
#     title="OpsFlow - Logistics Issue Automation",
#     description="Automated issue tracking system integrating Email, Slack, and Jira",
#     version="1.0.0"
# )

# app.include_router(demo_router, prefix="/demo")

# api_router = APIRouter(prefix="/api")

# settings = get_settings()
# mongo_client = AsyncIOMotorClient(settings.mongo_url)
# db = mongo_client[settings.db_name]

# app.add_middleware(
#     CORSMiddleware,
#     allow_credentials=True,
#     allow_origins=settings.cors_origins.split(','),
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @api_router.get("/")
# async def root():
#     return {
#         "service": "OpsFlow",
#         "status": "running",
#         "version": "1.0.0",
#         "features": [
#             "Email → Jira workflow",
#             "Jira → Email auto-response",
#             "Slack → Jira workflow",
#             "Jira → Slack thread reply",
#             "AI-powered categorization"
#         ]
#     }

# @api_router.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "database": "connected",
#         "email": "configured" if settings.email_username else "not configured",
#         "jira": "configured" if settings.jira_api_token else "not configured",
#         "slack": "configured" if settings.slack_bot_token else "not configured"
#     }

# @api_router.post("/test/email-poll")
# async def trigger_email_poll():
#     """Manually trigger email polling (for testing)."""
#     await email_poller.process_emails()
#     return {"status": "Email polling triggered"}

# api_router.include_router(webhooks.router)
# api_router.include_router(config_routes.router)
# api_router.include_router(mapping_routes.router)

# app.include_router(api_router)

# @app.on_event("startup")
# async def startup_event():
#     """Initialize services on startup."""
#     logger.info("=== OpsFlow Starting ===")
#     logger.info(f"Database: {settings.db_name}")
#     logger.info(f"Email configured: {bool(settings.email_username)}")
#     logger.info(f"Jira configured: {bool(settings.jira_api_token)}")
#     logger.info(f"Slack configured: {bool(settings.slack_bot_token)}")
    
#     email_poller.start()
#     logger.info("Email poller started")
    
#     try:
#         await db.command("ping")
#         logger.info("MongoDB connection successful")
#     except Exception as e:
#         logger.error(f"MongoDB connection failed: {str(e)}")
    
#     logger.info("=== OpsFlow Ready ===")

# @app.on_event("shutdown")
# async def shutdown_event():
#     """Cleanup on shutdown."""
#     logger.info("Shutting down OpsFlow...")
#     email_poller.stop()
#     mongo_client.close()
#     logger.info("OpsFlow shut down complete")


from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import logging
import json
import asyncio

# Config
from config import get_settings

# Routes
from routes import webhooks, config_routes, mapping_routes, tickets
from routes.demo import router as demo_router
from routes import analytics

# Jobs
from jobs.email_poller import email_poller


# -------------------- ENV + LOGGING --------------------

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# -------------------- APP INIT --------------------

app = FastAPI(
    title="OpsFlow - Logistics Issue Automation",
    description="Automated issue tracking system integrating Email, Slack, and Jira",
    version="1.0.0"
)

# Demo routes (no /api prefix)
app.include_router(demo_router, prefix="/demo")


# -------------------- SETTINGS + DB --------------------

settings = get_settings()

mongo_client = AsyncIOMotorClient(settings.mongo_url)
db = mongo_client[settings.db_name]


# -------------------- MIDDLEWARE --------------------

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------- API ROUTER --------------------

api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {
        "service": "OpsFlow",
        "status": "running",
        "version": "1.0.0",
        "features": [
            "Email → Jira workflow",
            "Jira → Email auto-response",
            "Slack → Jira workflow",
            "Jira → Slack thread reply",
            "AI-powered categorization"
        ]
    }


@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "email": "configured" if settings.email_username else "not configured",
        "jira": "configured" if settings.jira_api_token else "not configured",
        "slack": "configured" if settings.slack_bot_token else "not configured"
    }


@api_router.post("/test/email-poll")
async def trigger_email_poll():
    """Manually trigger email polling (for testing)."""
    await email_poller.process_emails()
    return {"status": "Email polling triggered"}


# -------------------- INCLUDE ROUTES --------------------

api_router.include_router(webhooks.router)
api_router.include_router(config_routes.router)
api_router.include_router(mapping_routes.router)
api_router.include_router(tickets.router)   # ✅ NEW (IMPORTANT)
api_router.include_router(analytics.router)  # Analytics endpoints

app.include_router(api_router)


# -------------------- WEBSOCKET --------------------

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message, default=str))
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

ws_manager = ConnectionManager()

@app.websocket("/api/ws/tickets")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

# Make ws_manager available globally
import builtins
builtins.ws_manager = ws_manager


# -------------------- STARTUP --------------------

@app.on_event("startup")
async def startup_event():
    logger.info("=== OpsFlow Starting ===")
    logger.info(f"Database: {settings.db_name}")
    logger.info(f"Email configured: {bool(settings.email_username)}")
    logger.info(f"Jira configured: {bool(settings.jira_api_token)}")
    logger.info(f"Slack configured: {bool(settings.slack_bot_token)}")

    email_poller.start()
    logger.info("Email poller started")

    try:
        await db.command("ping")
        logger.info("MongoDB connection successful")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {str(e)}")

    logger.info("=== OpsFlow Ready ===")


# -------------------- SHUTDOWN --------------------

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down OpsFlow...")
    email_poller.stop()
    mongo_client.close()
    logger.info("OpsFlow shut down complete")