# Meta WhatsApp Cloud API Integration Guide

ReachOut SMB integrates with the official Meta WhatsApp Business Platform (Cloud API) using Meta Graph API v26.0 (current official supported version).

## Meta Architecture Setup

1. **Meta Business Portfolio & WABA**:
   - Create or open your Meta Business Portfolio at [business.facebook.com](https://business.facebook.com).
   - Navigate to **WhatsApp Accounts** and create a WhatsApp Business Account (WABA).

2. **Dedicated Business Phone Number**:
   - Register a dedicated phone number (must not be active on a consumer WhatsApp account).
   - Complete SMS/voice verification inside the Meta Business Manager.

3. **Required Meta Permissions / Scopes**:
   - `whatsapp_business_management`: Manage WABA configuration and templates.
   - `whatsapp_business_messaging`: Send and receive live WhatsApp messages and media.

4. **Required Credentials**:
   In `.env`:
   ```env
   META_GRAPH_API_VERSION=v26.0
   WHATSAPP_ACCESS_TOKEN=<SYSTEM_USER_PERMANENT_ACCESS_TOKEN>
   WHATSAPP_BUSINESS_ACCOUNT_ID=<WABA_ID>
   WHATSAPP_PHONE_NUMBER_ID=<PHONE_NUMBER_ID>
   WHATSAPP_VERIFY_TOKEN=reachout_whatsapp_verify_token_2026
   WHATSAPP_APP_SECRET=<APP_SECRET>
   ```

5. **Webhook Configuration**:
   - Callback URL: `https://<YOUR_DOMAIN>/api/v1/webhooks/whatsapp`
   - Verify Token: Matches `WHATSAPP_VERIFY_TOKEN`.
   - Field Subscriptions: `messages`.

6. **Outbound Cloud API Examples (v26.0)**:
   - **Text**:
     ```http
     POST https://graph.facebook.com/v26.0/<PHONE_NUMBER_ID>/messages
     Authorization: Bearer <WHATSAPP_ACCESS_TOKEN>
     Content-Type: application/json
     {
       "messaging_product": "whatsapp",
       "to": "919876543210",
       "type": "text",
       "text": { "body": "Undi anna 😊 ₹1,299. Meeku photo pampinchana?" }
     }
     ```
   - **Image**:
     ```http
     POST https://graph.facebook.com/v26.0/<PHONE_NUMBER_ID>/messages
     Authorization: Bearer <WHATSAPP_ACCESS_TOKEN>
     Content-Type: application/json
     {
       "messaging_product": "whatsapp",
       "to": "919876543210",
       "type": "image",
       "image": {
         "link": "https://<PUBLIC_STORAGE_URL>/saree.jpg",
         "caption": "Crimson Kanjeevaram Silk Saree - ₹1,299"
       }
     }
     ```
