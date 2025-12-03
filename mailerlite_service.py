import httpx
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MailerliteService:
    def __init__(self, api_key: str, active_group_id: Optional[str] = None, cancelled_group_id: Optional[str] = None):
        self.api_key = api_key
        self.active_group_id = active_group_id
        self.cancelled_group_id = cancelled_group_id
        self.base_url = "https://connect.mailerlite.com/api"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def create_or_update_subscriber(
        self,
        email: str,
        first_name: str,
        last_name: str,
        membership_title: str,
        membership_id: int,
        subscription_id: str,
        price: str,
        period: str,
        period_type: str
    ) -> dict:
        """
        Creates or updates a subscriber in Mailerlite with custom fields and groups
        """
        try:
            # Prepare subscriber data with custom fields
            subscriber_data = {
                "email": email,
                "fields": {
                    "name": f"{first_name} {last_name}",
                    "last_name": last_name,
                },
                "groups": [],
                "status": "active"
            }

            # Add custom fields for membership info
            # Note: These custom fields need to be created in Mailerlite first
            subscriber_data["fields"].update({
                "membership_title": membership_title,
                "membership_id": str(membership_id),
                "subscription_id": subscription_id,
                "subscription_price": price,
                "subscription_period": f"{period} {period_type}"
            })

            # Add to active group if specified
            if self.active_group_id:
                subscriber_data["groups"].append(self.active_group_id)

            async with httpx.AsyncClient() as client:
                # Create or update subscriber
                response = await client.post(
                    f"{self.base_url}/subscribers",
                    headers=self.headers,
                    json=subscriber_data,
                    timeout=30.0
                )

                response.raise_for_status()
                subscriber = response.json()

                logger.info(f"Subscriber created/updated: {email}")

                # Add tag for the specific membership
                await self._add_tag(
                    client,
                    subscriber["data"]["id"],
                    f"membership_{membership_id}"
                )

                # Add tag for subscription status
                await self._add_tag(
                    client,
                    subscriber["data"]["id"],
                    "active_subscription"
                )

                return subscriber

        except httpx.HTTPStatusError as e:
            logger.error(f"Mailerlite API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error creating subscriber: {str(e)}")
            raise

    async def _add_tag(self, client: httpx.AsyncClient, subscriber_id: str, tag_name: str):
        """
        Adds a tag to a subscriber
        """
        try:
            response = await client.post(
                f"{self.base_url}/subscribers/{subscriber_id}/tags",
                headers=self.headers,
                json={"name": tag_name},
                timeout=30.0
            )
            response.raise_for_status()
            logger.info(f"Tag '{tag_name}' added to subscriber {subscriber_id}")
        except httpx.HTTPStatusError as e:
            logger.warning(f"Failed to add tag '{tag_name}': {e.response.status_code}")
        except Exception as e:
            logger.warning(f"Error adding tag: {str(e)}")

    async def remove_subscription_tag(self, email: str):
        """
        Removes active subscription tag (useful for subscription-cancelled events)
        """
        try:
            async with httpx.AsyncClient() as client:
                # Get subscriber by email
                response = await client.get(
                    f"{self.base_url}/subscribers/{email}",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                subscriber = response.json()

                # Remove active_subscription tag
                await client.delete(
                    f"{self.base_url}/subscribers/{subscriber['data']['id']}/tags/active_subscription",
                    headers=self.headers,
                    timeout=30.0
                )

                logger.info(f"Removed active_subscription tag from {email}")

        except Exception as e:
            logger.error(f"Error removing subscription tag: {str(e)}")
            raise

    async def handle_subscription_stopped(
        self,
        email: str,
        membership_id: int
    ):
        """
        Handles subscription stopped event:
        - Removes active_subscription tag
        - Adds subscription_stopped tag
        - Removes from active group
        - Adds to cancelled group
        """
        try:
            async with httpx.AsyncClient() as client:
                # Get subscriber by email
                response = await client.get(
                    f"{self.base_url}/subscribers/{email}",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                subscriber_data = response.json()
                subscriber_id = subscriber_data["data"]["id"]

                logger.info(f"Processing subscription stopped for {email} (subscriber ID: {subscriber_id})")

                # Remove active_subscription tag
                try:
                    await client.delete(
                        f"{self.base_url}/subscribers/{subscriber_id}/tags/active_subscription",
                        headers=self.headers,
                        timeout=30.0
                    )
                    logger.info(f"Removed active_subscription tag from {email}")
                except Exception as e:
                    logger.warning(f"Could not remove active_subscription tag: {str(e)}")

                # Add subscription_stopped tag
                await self._add_tag(client, subscriber_id, "subscription_stopped")

                # Add membership-specific stopped tag
                await self._add_tag(client, subscriber_id, f"membership_{membership_id}_stopped")

                # Remove from active group and add to cancelled group
                if self.active_group_id and self.cancelled_group_id:
                    # Remove from active group
                    try:
                        await client.delete(
                            f"{self.base_url}/subscribers/{subscriber_id}/groups/{self.active_group_id}",
                            headers=self.headers,
                            timeout=30.0
                        )
                        logger.info(f"Removed {email} from active group {self.active_group_id}")
                    except Exception as e:
                        logger.warning(f"Could not remove from active group: {str(e)}")

                    # Add to cancelled group
                    try:
                        await client.post(
                            f"{self.base_url}/subscribers/{subscriber_id}/groups/{self.cancelled_group_id}",
                            headers=self.headers,
                            timeout=30.0
                        )
                        logger.info(f"Added {email} to cancelled group {self.cancelled_group_id}")
                    except Exception as e:
                        logger.warning(f"Could not add to cancelled group: {str(e)}")

                logger.info(f"Successfully processed subscription stopped for {email}")

        except Exception as e:
            logger.error(f"Error handling subscription stopped: {str(e)}")
            raise
