# LinkedIn Plugin for Dify

**Author:** Abhishek
**Version:** 0.0.2
**Type:** Social Media Tool

Unlock the power of your professional network with the LinkedIn plugin for Dify. This tool enables your AI agents and workflows to publish high-quality content, share articles, and engage with your audience on LinkedIn seamlessly.

## Key Features
- **Profile Updates**: Post text-based updates to your professional profile.
- **Article Sharing**: Share URLs with custom descriptions.
- **Media Support**: (Experimental) Robust handling for image uploads and media registration.
- **Organization Support**: Post as a LinkedIn Page (Organization) using URN identifiers.

## Prerequisites

To use this plugin, you need a LinkedIn Developer account and an App.

### 1. Create a LinkedIn App
1. Go to the [LinkedIn Developers Portal](https://www.linkedin.com/developers/apps).
2. Click **Create app**.
3. Fill in the required details and link it to your LinkedIn Page.

### 2. Configure Permissions (Products)
In your app settings, under the **Products** tab, request:
- **Share on LinkedIn**: Provides `w_member_social` for personal posts.
- **Advertising API** (optional): May be required for some organization features.

### 3. Authentication Setup
1. Go to the **Auth** tab.
2. Note your **Client ID** and **Client Secret**.
3. Add the **OAuth 2.0 Redirect URL** provided by your Dify instance.
   - Typically: `https://<your-dify-domain>/console/api/workspaces/current/tool-provider/oauth/callback`

## Installation

1. Package the plugin: `difypkg package linkedin/`
2. Upload the `.difypkg` file to your Dify instance under **Plugins**.
3. Configure the tool with your Client ID and Client Secret.
4. Complete the OAuth flow to authorize the plugin.

## Usage

Use the `share_update` tool within your Agent or Workflow. You can specify:
- `content`: The text of your post.
- `visibility`: `PUBLIC` (default) or `CONNECTIONS`.
- `media_url`: (Optional) URL of an image to attach.
- `owner_urn`: (Optional) The URN of the organization or person if different from the authenticated user.

## Troubleshooting

- **Invalid Redirect URL**: Ensure the redirect URL in Dify matches exactly what is registered in the LinkedIn Developer Portal.
- **Permissions Error**: Verify that "Share on LinkedIn" is active in your app's Products tab.
- **Media Upload Failures**: Ensure the `media_url` is publicly accessible.

---
*Created by Abhishek as a Dify Community Contribution.*
