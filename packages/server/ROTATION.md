# API Key Rotation Guide for Paperclip Companies

This guide details the process for rotating your `SUPRAWALL_API_KEY` within a Paperclip company environment to maintain continuous security without interrupting agent operations.

## Overview

Your Paperclip company uses the `SUPRAWALL_API_KEY` to authenticate with the SupraWall Vault. Rotating this key is essential if you suspect a leak, or as part of a regular security hygiene schedule (e.g., every 90 days).

---

## Zero-Downtime Rotation Process

To ensure your agents never fail to resolve credentials, follow this "Shadow Key" rotation pattern:

### 1. Generate a New Master Key
In your SupraWall Dashboard (or via Admin API), generate a new Master API key for your tenant.
*   **Do NOT delete the old key yet.** SupraWall supports multiple active master keys per tenant for this exact reason.

### 2. Update Paperclip Secrets
Push the new key to your Paperclip company's encrypted secrets store. This will overwrite the old key in the environment, but Paperclip's internal cache may still hold the old one for a few seconds.

```bash
curl -X POST https://api.paperclipai.com/api/companies/{YOUR_COMPANY_ID}/secrets \
  -H "Authorization: Bearer {YOUR_PAPERCLIP_ADMIN_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SUPRAWALL_API_KEY",
    "value": "sw_admin_NEW_KEY_VALUE_HERE",
    "provider": "local_encrypted"
  }'
```

### 3. Verify Agent Health
Monitor your SupraWall Audit Logs. You should see a mix of requests using the old hash and the new hash. Once 100% of traffic is coming from the new hash (usually after 1-2 minutes or a container restart), proceed to step 4.

### 4. Revoke the Old Key
In the SupraWall Dashboard:
1. Locate the old API key (identifiable by the truncated prefix and last-used timestamp).
2. Click **Revoke**. 
3. Any lingering requests with the old key will now receive a `401 Unauthorized` response.

---

## Temporary Key Rotation (Onboarding)

If you are still in the onboarding phase and using a `sw_temp_` key:
1. Complete the [Activation Flow](https://supra-wall.com/activate).
2. Once activated, you will be issued a permanent `sw_admin_` key.
3. Replace the `sw_temp_` key in your Paperclip secrets immediately.

## Emergency Revocation

If you know a key is compromised:
1. **Revoke Immediately** in the SupraWall Dashboard.
2. **Accept Downtime**: Agents will fail tasks until a new key is provided in Step 2.
3. This is preferred over allowing a malicious actor to exfiltrate vault credentials.

---

## Support
For assistance with complex rotations or automated key management via Terraform/Vault, contact `security@wiserautomation.agency`.
