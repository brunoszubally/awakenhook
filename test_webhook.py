"""
Test script to simulate Memberpress webhook calls
Usage: python test_webhook.py
"""
import httpx
import asyncio
import json


async def test_subscription_created():
    """Test subscription-created webhook"""

    webhook_data = {
        "event": "subscription-created",
        "type": "subscription",
        "data": {
            "coupon": False,
            "membership": {
                "id": 1257,
                "title": "Awaken Hungary Academy",
                "content": "",
                "excerpt": "",
                "date": "2024-07-27 15:10:04",
                "status": "publish",
                "author": "33",
                "date_gmt": "2024-07-27 15:10:04",
                "modified": "2025-08-01 08:24:05",
                "modified_gmt": "2025-08-01 06:24:05",
                "group": "0",
                "price": "12490.00",
                "period": "1",
                "period_type": "months",
                "signup_button_text": "Csatlakozom az Academyhez"
            },
            "member": {
                "id": 2470,
                "email": "test@example.com",
                "username": "testuser@example.com",
                "nicename": "testuser-example-com",
                "url": "",
                "message": "",
                "registered_at": "2025-12-01 22:24:17",
                "first_name": "Test",
                "last_name": "User",
                "display_name": "Test User"
            },
            "id": "3245",
            "subscr_id": "sub_test123456789",
            "gateway": "scvlz8-ji",
            "price": "12490.00",
            "period": "1",
            "period_type": "months",
            "limit_cycles": "0",
            "limit_cycles_num": "2",
            "limit_cycles_action": "expire",
            "limit_cycles_expires_after": "1",
            "limit_cycles_expires_type": "days",
            "prorated_trial": "0",
            "trial": "0",
            "trial_days": "0",
            "trial_amount": "990.00",
            "trial_tax_amount": "0.00",
            "trial_tax_reversal_amount": "0.00",
            "trial_total": "0.00",
            "status": "active",
            "created_at": "2025-12-01 22:25:24",
            "total": "12490.00",
            "tax_rate": "0.000",
            "tax_amount": "0.00",
            "tax_reversal_amount": "0.00",
            "tax_desc": "",
            "tax_class": "standard",
            "cc_last4": "6618",
            "cc_exp_month": "6",
            "cc_exp_year": "2026",
            "token": "",
            "order_id": "0",
            "tax_compound": "0",
            "tax_shipping": "1",
            "response": None
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/webhook/memberpress",
                json=webhook_data,
                timeout=30.0
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")

            if response.status_code == 200:
                print("\n✅ Webhook test successful!")
            else:
                print("\n❌ Webhook test failed!")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


async def test_subscription_stopped():
    """Test subscription-stopped webhook"""

    webhook_data = {
        "event": "subscription-stopped",
        "type": "subscription",
        "data": {
            "coupon": False,
            "membership": {
                "id": 3006,
                "title": "Teremtő levelek",
                "content": "",
                "excerpt": "",
                "date": "2025-10-20 18:35:09",
                "status": "publish",
                "author": "345",
                "date_gmt": "2025-10-20 16:35:09",
                "modified": "2025-10-20 18:36:41",
                "modified_gmt": "2025-10-20 16:36:41",
                "group": "0",
                "price": "1990.00",
                "period": "1",
                "period_type": "months",
                "signup_button_text": "Feliratkozás"
            },
            "member": {
                "id": 2401,
                "email": "test@example.com",
                "username": "test@example.com",
                "nicename": "test-example-com",
                "url": "",
                "message": "",
                "registered_at": "2025-11-02 17:32:02",
                "first_name": "Test",
                "last_name": "User",
                "display_name": "Test User"
            },
            "id": "3121",
            "subscr_id": "sub_test_stopped_123",
            "gateway": "scvlz8-ji",
            "price": "1990.00",
            "period": "1",
            "period_type": "months",
            "limit_cycles": "0",
            "limit_cycles_num": "2",
            "limit_cycles_action": "expire",
            "limit_cycles_expires_after": "1",
            "limit_cycles_expires_type": "days",
            "prorated_trial": "0",
            "trial": "0",
            "trial_days": "0",
            "trial_amount": "0.00",
            "trial_tax_amount": "0.00",
            "trial_tax_reversal_amount": "0.00",
            "trial_total": "0.00",
            "status": "cancelled",
            "created_at": "2025-11-02 17:32:26",
            "total": "1990.00",
            "tax_rate": "0.000",
            "tax_amount": "0.00",
            "tax_reversal_amount": "0.00",
            "tax_desc": "",
            "tax_class": "standard",
            "cc_last4": "5370",
            "cc_exp_month": "11",
            "cc_exp_year": "2026",
            "token": "",
            "order_id": "0",
            "tax_compound": "0",
            "tax_shipping": "1",
            "response": None
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/webhook/memberpress",
                json=webhook_data,
                timeout=30.0
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")

            if response.status_code == 200:
                print("\n✅ Webhook test successful!")
            else:
                print("\n❌ Webhook test failed!")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    import sys

    print("Testing Memberpress webhook...")
    print("Make sure the service is running on http://localhost:8000\n")

    if len(sys.argv) > 1 and sys.argv[1] == "stopped":
        print("Testing subscription-stopped event...\n")
        asyncio.run(test_subscription_stopped())
    else:
        print("Testing subscription-created event...")
        print("(Use 'python test_webhook.py stopped' to test subscription-stopped)\n")
        asyncio.run(test_subscription_created())
