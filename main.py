from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings
from typing import Optional
import logging
from contextlib import asynccontextmanager

from models import MemberpressWebhook
from mailerlite_service import MailerliteService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    mailerlite_api_key: str
    mailerlite_active_group_id: Optional[str] = None
    mailerlite_cancelled_group_id: Optional[str] = None
    memberpress_webhook_secret: Optional[str] = None
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
mailerlite = MailerliteService(
    api_key=settings.mailerlite_api_key,
    active_group_id=settings.mailerlite_active_group_id,
    cancelled_group_id=settings.mailerlite_cancelled_group_id
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Awaken Hook service...")
    logger.info(f"Mailerlite API configured: {'Yes' if settings.mailerlite_api_key else 'No'}")
    logger.info(f"Active Group ID: {settings.mailerlite_active_group_id or 'Not set'}")
    logger.info(f"Cancelled Group ID: {settings.mailerlite_cancelled_group_id or 'Not set'}")
    yield
    logger.info("Shutting down Awaken Hook service...")


app = FastAPI(
    title="Awaken Hook",
    description="Memberpress to Mailerlite webhook integration",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "service": "Awaken Hook",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mailerlite_configured": bool(settings.mailerlite_api_key)
    }


@app.post("/webhook/memberpress")
async def memberpress_webhook(webhook: MemberpressWebhook, request: Request):
    """
    Receives Memberpress webhook events and processes them
    """
    try:
        logger.info(f"Received webhook event: {webhook.event}")
        logger.info(f"Event type: {webhook.type}")
        logger.info(f"Member: {webhook.data.member.email}")

        # Handle different event types
        if webhook.event == "subscription-created":
            await handle_subscription_created(webhook)
        elif webhook.event == "subscription-cancelled":
            await handle_subscription_cancelled(webhook)
        elif webhook.event == "subscription-stopped":
            await handle_subscription_stopped(webhook)
        elif webhook.event == "subscription-paused":
            await handle_subscription_paused(webhook)
        elif webhook.event == "subscription-resumed":
            await handle_subscription_resumed(webhook)
        else:
            logger.warning(f"Unhandled event type: {webhook.event}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": f"Event {webhook.event} processed successfully"
            }
        )

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )


async def handle_subscription_created(webhook: MemberpressWebhook):
    """
    Handles subscription-created event
    Creates/updates subscriber in Mailerlite with all relevant data
    """
    logger.info(f"Processing subscription creation for {webhook.data.member.email}")

    try:
        result = await mailerlite.create_or_update_subscriber(
            email=webhook.data.member.email,
            first_name=webhook.data.member.first_name,
            last_name=webhook.data.member.last_name,
            membership_title=webhook.data.membership.title,
            membership_id=webhook.data.membership.id,
            subscription_id=webhook.data.subscr_id,
            price=webhook.data.price,
            period=webhook.data.period,
            period_type=webhook.data.period_type
        )

        logger.info(f"Successfully created/updated subscriber in Mailerlite: {webhook.data.member.email}")
        return result

    except Exception as e:
        logger.error(f"Failed to process subscription creation: {str(e)}")
        raise


async def handle_subscription_cancelled(webhook: MemberpressWebhook):
    """
    Handles subscription-cancelled event
    Removes active subscription tag from subscriber
    """
    logger.info(f"Processing subscription cancellation for {webhook.data.member.email}")

    try:
        await mailerlite.remove_subscription_tag(webhook.data.member.email)
        logger.info(f"Successfully processed subscription cancellation: {webhook.data.member.email}")

    except Exception as e:
        logger.error(f"Failed to process subscription cancellation: {str(e)}")
        raise


async def handle_subscription_stopped(webhook: MemberpressWebhook):
    """
    Handles subscription-stopped event
    - Removes active_subscription tag
    - Adds subscription_stopped tag
    - Removes from active group
    - Adds to cancelled group
    """
    logger.info(f"Processing subscription stopped for {webhook.data.member.email}")

    try:
        await mailerlite.handle_subscription_stopped(
            email=webhook.data.member.email,
            membership_id=webhook.data.membership.id
        )
        logger.info(f"Successfully processed subscription stopped: {webhook.data.member.email}")

    except Exception as e:
        logger.error(f"Failed to process subscription stopped: {str(e)}")
        raise


async def handle_subscription_paused(webhook: MemberpressWebhook):
    """
    Handles subscription-paused event
    """
    logger.info(f"Processing subscription pause for {webhook.data.member.email}")
    # Implement custom logic for paused subscriptions if needed
    pass


async def handle_subscription_resumed(webhook: MemberpressWebhook):
    """
    Handles subscription-resumed event
    """
    logger.info(f"Processing subscription resume for {webhook.data.member.email}")
    # Implement custom logic for resumed subscriptions if needed
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
