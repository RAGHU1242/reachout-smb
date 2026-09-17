# Meta Instagram Messaging Integration Guide

ReachOut SMB uses the official Meta Graph API v21.0+ Instagram Messaging API with Instagram Login for Professional Accounts.

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
   *(Do not use deprecated permissions like business_basic or legacy permissions)*.

4. **Configure Webhook**:
   - Webhook URL: `https://<YOUR_DOMAIN>/api/v1/webhooks/instagram`
   - Verify Token: Matches `INSTAGRAM_VERIFY_TOKEN` in `.env` (e.g. `reachout_instagram_verify_token_2026`).
   - Subscribe to field: `messages`, `messaging_postbacks`, `message_deliveries`.

5. **Connecting an Instagram Professional Account**:
   - Ensure the Instagram account is set to **Professional (Business or Creator)**.
   - Connect the Instagram account to your Facebook Page.
   - In ReachOut SMB Dashboard -> **Settings -> Integrations**, click **Connect Instagram**.

6. **Outbound Messaging Format**:
   - **Text Messages**:
     ```http
     POST https://graph.facebook.com/v21.0/me/messages
     Authorization: Bearer <PAGE_OR_USER_ACCESS_TOKEN>
     {
       "recipient": {"id": "<IGSID>"},
       "message": {"text": "Undi 😊 ₹1,299. Meeku photo pampinchana?"}
     }
     ```
   - **Product Image Messages**:
     ```http
     POST https://graph.facebook.com/v21.0/me/messages
     Authorization: Bearer <PAGE_OR_USER_ACCESS_TOKEN>
     {
       "recipient": {"id": "<IGSID>"},
       "message": {
         "attachment": {
           "type": "image",
           "payload": {
             "url": "https://<STORAGE_URL>/saree.jpg",
             "is_reusable": true
           }
         }
       }
     }
     ```
