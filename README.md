# Awaken Hook

Memberpress webhook service that automatically syncs subscription data to Mailerlite.

## Features

- Receives Memberpress webhook events
- Creates/updates subscribers in Mailerlite
- Adds subscribers to specified groups
- Tags subscribers based on membership and subscription status
- Stores membership data in custom fields
- Handles multiple subscription events (created, cancelled, paused, resumed)

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
MAILERLITE_API_KEY=your_mailerlite_api_key_here
MAILERLITE_ACTIVE_GROUP_ID=your_active_group_id_here
MAILERLITE_CANCELLED_GROUP_ID=your_cancelled_group_id_here
MEMBERPRESS_WEBHOOK_SECRET=your_webhook_secret_here  # Optional
HOST=0.0.0.0
PORT=8000
```

### 3. Get Mailerlite Credentials

#### API Key
1. Log in to your Mailerlite account
2. Go to Integrations > Developer API
3. Generate a new API key
4. Copy the key to `MAILERLITE_API_KEY` in `.env`

#### Group IDs
You need to create two groups in Mailerlite:

**Active Group** (for active subscriptions):
1. In Mailerlite, go to Subscribers > Groups
2. Create a group called "Active Subscriptions" (or any name you prefer)
3. Click on the group
4. The Group ID is in the URL: `https://dashboard.mailerlite.com/groups/{GROUP_ID}/subscribers`
5. Copy the Group ID to `MAILERLITE_ACTIVE_GROUP_ID` in `.env`

**Cancelled Group** (for stopped/cancelled subscriptions):
1. Create another group called "Cancelled Subscriptions" (or any name you prefer)
2. Click on the group
3. Copy the Group ID to `MAILERLITE_CANCELLED_GROUP_ID` in `.env`

### 4. Create Custom Fields in Mailerlite

Before running the service, create these custom fields in Mailerlite:

1. Go to Subscribers > Custom fields
2. Create the following fields:
   - `membership_title` (Text)
   - `membership_id` (Text)
   - `subscription_id` (Text)
   - `subscription_price` (Text)
   - `subscription_period` (Text)

## Running the Service

### Development Mode (Local)

```bash
python main.py
```

The service will start on `http://localhost:8000`

### Production Deployment on Render.com

#### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/awakenhook.git
git push -u origin main
```

#### 2. Deploy on Render.com

1. Go to [Render.com](https://render.com) and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Click "Apply" to create the service

#### 3. Configure Environment Variables

After the service is created, go to the service dashboard and add these environment variables:

- `MAILERLITE_API_KEY` - Your Mailerlite API key
- `MAILERLITE_ACTIVE_GROUP_ID` - Group ID for active subscriptions
- `MAILERLITE_CANCELLED_GROUP_ID` - Group ID for cancelled subscriptions
- `MEMBERPRESS_WEBHOOK_SECRET` - (Optional) Webhook secret for security

#### 4. Get Your Webhook URL

Once deployed, your webhook URL will be:
```
https://awakenhook.onrender.com/webhook/memberpress
```

Use this URL in your Memberpress webhook configuration.

## Configure Memberpress Webhook

1. Log in to your WordPress admin panel
2. Go to Memberpress > Settings > Webhooks
3. Click "Add Webhook"
4. Configure:
   - **URL**: `https://your-domain.com/webhook/memberpress`
   - **Event**: Select the events you want to track:
     - `subscription-created`
     - `subscription-cancelled`
     - `subscription-stopped`
     - `subscription-paused`
     - `subscription-resumed`
5. Save the webhook

### Testing the Webhook

You can test the webhook locally using ngrok:

```bash
# Install ngrok if you don't have it
brew install ngrok  # On macOS

# Start the service
python main.py

# In another terminal, start ngrok
ngrok http 8000

# Use the ngrok URL in Memberpress webhook settings
# Example: https://abc123.ngrok.io/webhook/memberpress
```

## API Endpoints

### Health Check

```bash
GET /health
```

Returns the service status and configuration.

### Webhook Endpoint

```bash
POST /webhook/memberpress
```

Receives Memberpress webhook events.

## What Happens When a Subscription is Created

1. Memberpress sends webhook to `/webhook/memberpress`
2. Service validates the webhook data
3. Service creates/updates subscriber in Mailerlite with:
   - Email address
   - First name and last name
   - Membership details (title, ID, price, period)
   - Subscription ID
4. Adds subscriber to the active group
5. Adds tags:
   - `membership_{id}` (e.g., `membership_1257`)
   - `active_subscription`
6. Returns success response to Memberpress

## What Happens When a Subscription is Stopped

1. Memberpress sends `subscription-stopped` webhook to `/webhook/memberpress`
2. Service validates the webhook data
3. Service updates the subscriber in Mailerlite:
   - **Removes** `active_subscription` tag
   - **Adds** `subscription_stopped` tag
   - **Adds** `membership_{id}_stopped` tag (e.g., `membership_3006_stopped`)
   - **Removes** subscriber from active group
   - **Adds** subscriber to cancelled group
4. Returns success response to Memberpress

This allows you to:
- Segment your email campaigns based on subscription status
- Send re-engagement campaigns to cancelled subscribers
- Track which memberships were cancelled

## Monitoring

Check the logs for webhook processing:

```bash
# The service logs all webhook events and Mailerlite API calls
# Look for lines like:
# INFO - Received webhook event: subscription-created
# INFO - Subscriber created/updated: user@example.com
# INFO - Tag 'membership_1257' added to subscriber
```

## Troubleshooting

### Webhook not received

- Check that your server is accessible from the internet
- Verify the webhook URL in Memberpress settings
- Check firewall rules

### Mailerlite API errors

- Verify your API key is correct
- Check that custom fields exist in Mailerlite
- Verify the group ID is correct
- Check Mailerlite API rate limits

### Missing custom fields

If you see errors about missing fields, make sure all custom fields are created in Mailerlite before processing webhooks.

## Security

### Webhook Signature Verification (Optional)

To enable webhook signature verification:

1. Get your webhook secret from Memberpress
2. Add it to `.env` as `MEMBERPRESS_WEBHOOK_SECRET`
3. The service will verify webhook signatures automatically

## License

MIT
