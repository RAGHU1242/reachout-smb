# Meta Instagram Messaging Integration Guide

ReachOut SMB uses the official Meta Graph API v26.0 (current official supported version) Instagram Messaging API with Instagram Login for Professional Accounts.

## Step-by-Step Meta Developer Setup

1. **Meta Developer Portal**:
   - Go to [developers.facebook.com](https://developers.facebook.com) and create or select an App.
   - Choose **Business** or **Other** app type.

2. **Add Instagram Product**:
   - Add the **Instagram** product to your App.
   - Configure **Instagram Messaging** under Settings.

3. **Required Scopes & Permissions**:
   - `instagram_business_basic`: Access basic profile information.
   - `instagram_business_manage_messages`: Read and send direct messages, media, and quick replies.
   *(Do not use deprecated permission names like business_basic or legacy permissions)*.

4. **Configure Webhook**:
   - Webhook URL: `https://<YOUR_DOMAIN>/api/v1/webhooks/instagram`
   - Verify Token: Matches `INSTAGRAM_VERIFY_TOKEN` in `.env` (e.g. `reachout_instagram_verify_token_2026`).
   - Subscribe to field: `messages`, `messaging_postbacks`, `message_deliveries`.

5. **Connecting an Instagram Professional Account**:
   - Ensure the Instagram account is set to **Professional (Business or Creator)**.
   - Connect the Instagram account to your Facebook Page.
   - In ReachOut SMB Dashboard -> **Settings -> Integrations**, click **Connect Instagram**.

6. **Outbound Messaging Format (Graph API v26.0)**:
   - **Text Messages**:
     ```http
     POST https://graph.facebook.com/v26.0/me/messages
     Authorization: Bearer <PAGE_OR_USER_ACCESS_TOKEN>
     {
       "recipient": {"id": "<IGSID>"},
       "message": {"text": "Undi 😊 ₹1,299. Meeku photo pampinchana?"}
     }
     ```
   - **Product Image Messages**:
     ```http
     POST https://graph.facebook.com/v26.0/me/messages
     Authorization: Bearer <PAGE_OR_USER_ACCESS_TOKEN>
     {
       "recipient": {"id": "<IGSID>"},
       "message": {
         "attachment": {
           "type": "image",
           "payload": {
             "url": "https://<PUBLIC_STORAGE_URL>/saree.jpg",
             "is_reusable": true
           }
         }
       }
     }
     ```

## Live Instagram Test Procedure

To verify the live Instagram message flow with real accounts:
1. **Account A (Merchant)**: Ensure your connected Instagram Professional account has active webhooks subscribed to `https://<YOUR_DOMAIN>/api/v1/webhooks/instagram`.
2. **Account B (Customer)**: From any personal Instagram account, send a DM to Account A:
   `"Anna red saree undha?"`
3. **Verify Incoming Webhook**:
   - FastAPI receives the POST event with HMAC signature verification.
   - Idempotency is enforced by storing `event_id` in `webhook_events`.
   - Customer and conversation are created/retrieved under the tenant's business ID.
4. **Verify Outgoing Response**:
   - AI agent calls `search_products` tool.
   - Generates Telugu confirmation: `"ఉందండి 😊 మా దగ్గర అందమైన Crimson Kanjeevaram Silk Saree రెడీ స్టాక్ ఉంది! ధర: ₹1,299"`.
   - Sends the matching saree image attachment via the Meta Send API.
5. **Verify Delivery Calculation & Order**:
   - Customer replies: `"Delivery Miyapur?"`
   - AI calls `calculate_delivery` -> returns ₹50 delivery charge.
   - Customer replies: `"Okay book it. Flat 304, Miyapur, Hyderabad"`
   - AI calls `create_order` -> Order record is saved in database and instantly appears on `/orders` dashboard.
