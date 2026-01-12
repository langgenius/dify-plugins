from collections.abc import Generator
from typing import Any
import requests
import json
import time

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class LinkedinTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        content = tool_parameters.get("content")
        author_type = tool_parameters.get("author_type", "PERSON")
        organization_id = tool_parameters.get("organization_id")
        media_category = tool_parameters.get("media_category", "NONE")
        media_url = tool_parameters.get("media_url")
        media_title = tool_parameters.get("media_title")
        media_description = tool_parameters.get("media_description")
        visibility = tool_parameters.get("visibility", "PUBLIC")

        # DEBUG: Log the type of self.runtime as suggested by the debug guide
        print(f"DEBUG: type(self.runtime) = {type(self.runtime)}")
        
        # Access credentials robustly
        credentials = {}
        try:
            if hasattr(self.runtime, "credentials"):
                credentials = self.runtime.credentials
                print("DEBUG: Accessed credentials via attribute")
            elif isinstance(self.runtime, dict):
                credentials = self.runtime.get("credentials", {})
                print("DEBUG: Accessed credentials via dict key")
            else:
                # Direct access fallback
                print(f"DEBUG: Unexpected runtime type {type(self.runtime)}, attempting direct dict access if possible")
                if hasattr(self.runtime, "__getitem__"):
                    credentials = self.runtime.get("credentials", {})
                
            # Final fallback: maybe self.runtime IS the credentials dict?
            if not credentials or not credentials.get("access_token"):
                 if isinstance(self.runtime, dict) and self.runtime.get("access_token"):
                     credentials = self.runtime
                     print("DEBUG: Using self.runtime as credentials dict")
                 elif hasattr(self.runtime, "get") and self.runtime.get("access_token"):
                     credentials = self.runtime
                     print("DEBUG: Using self.runtime (object) as credentials mapping")
        except Exception as e:
            print(f"DEBUG: Error during credential extraction: {str(e)}")

        # Log the type of credentials
        print(f"DEBUG: type(credentials) = {type(credentials)}")

        if not credentials or (isinstance(credentials, dict) and not credentials.get("access_token")):
            raise ValueError(f"LinkedIn Access Token is missing. Runtime type: {type(self.runtime)}. Please authenticate first.")
            
        # Get access token safely
        if isinstance(credentials, dict):
            access_token = credentials.get("access_token")
        else:
            access_token = getattr(credentials, "access_token", None)
            
        if not access_token:
             raise ValueError("Failed to extract access_token from credentials.")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

        # 1. Determine Author URN
        if author_type == "ORGANIZATION":
            if not organization_id:
                yield self.create_text_message("Organization ID is required when posting as an Organization.")
                return
            # Ensure organization_id is just the numeric part if provided as URN
            org_id = organization_id.split(":")[-1] if ":" in organization_id else organization_id
            author_urn = f"urn:li:organization:{org_id}"
        else:
            # Person: Get User URN
            profile_url = "https://api.linkedin.com/v2/userinfo" # standard for OpenID Connect
            try:
                profile_response = requests.get(profile_url, headers=headers)
                if profile_response.status_code != 200:
                    # Fallback to /v2/me if userinfo fails
                    profile_response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
                
                profile_response.raise_for_status()
                profile_data = profile_response.json()
                # userinfo uses 'sub', /v2/me uses 'id'
                user_urn = profile_data.get("sub") or profile_data.get("id")
                
                if not user_urn:
                     yield self.create_text_message(f"Failed to retrieve User ID from LinkedIn profile. Response: {profile_data}")
                     return
                author_urn = f"urn:li:person:{user_urn}"
            except Exception as e:
                 yield self.create_text_message(f"Error fetching profile: {str(e)}")
                 return

        # 2. Prepare Share Content
        share_content = {
            "shareCommentary": {
                "text": content
            },
            "shareMediaCategory": media_category if media_category != "NONE" else "NONE"
        }
        
        if media_category == "ARTICLE":
            if not media_url:
                yield self.create_text_message("Media URL is required for ARTICLE type.")
                return
            
            media_item = {
                "status": "READY",
                "originalUrl": media_url
            }
            if media_title:
                media_item["title"] = {"text": media_title}
            if media_description:
                media_item["description"] = {"text": media_description}
                
            share_content["media"] = [media_item]
            
        elif media_category == "IMAGE":
            if not media_url:
                yield self.create_text_message("Media URL is required for IMAGE type.")
                return
            
            # Handle Image Upload
            try:
                print(f"DEBUG: Starting image upload from URL: {media_url}")
                asset_urn = self._upload_image(media_url, author_urn, headers)
                print(f"DEBUG: Image uploaded successfully. Asset URN: {asset_urn}")
                
                share_content["media"] = [{
                    "status": "READY",
                    "media": asset_urn,
                    "title": {"text": media_title or "Shared Image"},
                    "description": {"text": media_description or "Shared Image Content"}
                }]
            except Exception as e:
                 print(f"DEBUG: Image upload failed: {str(e)}")
                 yield self.create_text_message(f"Failed to upload image: {str(e)}")
                 return

        # 3. Create UGC Post
        post_url = "https://api.linkedin.com/v2/ugcPosts"
        visibility_code = "PUBLIC" if visibility == "PUBLIC" else "CONNECTIONS"
        
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": share_content
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility_code
            }
        }
        
        try:
            post_response = requests.post(post_url, headers=headers, json=payload)
            post_response.raise_for_status()
            post_data = post_response.json()
            
            post_id = post_data.get("id")
            # Post ID is often urn:li:share:123 or urn:li:ugcPost:123
            # To get a clickable link, we might need a different format, but this is a common approach.
            # LinkedIn post URNs look like urn:li:ugcPost:123 or urn:li:share:123
            # Numeric ID is the suffix
            numeric_id = post_id.split(":")[-1]
            
            # Construct multiple possible URLs for the user to try
            view_url = f"https://www.linkedin.com/feed/update/{post_id}"
            activity_url = f"https://www.linkedin.com/feed/update/urn:li:activity:{numeric_id}"
            direct_post_url = f"https://www.linkedin.com/posts/{numeric_id}"
            
            yield self.create_json_message({
                "status": "success",
                "post_id": post_id,
                "url": view_url,
                "alternative_urls": {
                    "activity_format": activity_url,
                    "direct_format": direct_post_url
                },
                "author": author_urn,
                "media_category": media_category,
                "message": "Successfully posted update to LinkedIn. If the main URL doesn't work immediately, try the alternative formats."
            })
            
        except requests.exceptions.HTTPError as e:
            error_content = e.response.text
            yield self.create_text_message(f"Failed to post update. HTTP Error: {str(e)}. Details: {error_content}")
        except Exception as e:
            yield self.create_text_message(f"An unexpected error occurred: {str(e)}")

    def _upload_image(self, image_url: str, author_urn: str, headers: dict) -> str:
        """
        Upload an image to LinkedIn and return the asset URN.
        """
        # Step 1: Register Upload
        register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        register_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": author_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        reg_response = requests.post(register_url, headers=headers, json=register_payload)
        reg_response.raise_for_status()
        reg_data = reg_response.json()
        
        upload_url = reg_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset_urn = reg_data['value']['asset']
        
        print(f"DEBUG: Registered upload. Asset: {asset_urn}, UploadURL present: {bool(upload_url)}")
        
        # Step 2: Download Image from URL
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        image_data = image_response.content
        print(f"DEBUG: Downloaded image data. Size: {len(image_data)} bytes")
        
        # Step 3: Upload to LinkedIn
        # IMPORTANT: For pre-signed URLs (like uploadUrl), extra headers can cause 403.
        # LinkedIn docs suggest only Content-Type is needed for the binary PUT.
        upload_headers = {
            "Content-Type": "application/octet-stream"
        }
        
        # Some implementations suggest still needing Authorization, but not the Restli protocol.
        # Let's try only with Content-Type as it's a signed URL.
        # If it fails, we'll try including Authorization but no Restli.
        
        put_response = requests.put(upload_url, headers=upload_headers, data=image_data)
        if put_response.status_code not in [200, 201]:
             # Fallback: Many examples show Authorization still needed
             print(f"DEBUG: Direct PUT failed with {put_response.status_code}, retrying with Authorization header")
             upload_headers["Authorization"] = headers.get("Authorization")
             put_response = requests.put(upload_url, headers=upload_headers, data=image_data)
        
        put_response.raise_for_status()
        print(f"DEBUG: Binary upload successful. Status: {put_response.status_code}")
        
        # Step 4: Poll for Asset Readiness (Crucial for visibility)
        print(f"DEBUG: Internal Asset Check for {asset_urn}")
        poll_start = time.time()
        while time.time() - poll_start < 30: # 30 seconds max
            try:
                asset_get_url = f"https://api.linkedin.com/v2/assets/{asset_urn}"
                check_response = requests.get(asset_get_url, headers=headers)
                if check_response.status_code == 200:
                    asset_info = check_response.json()
                    status = asset_info.get("status")
                    print(f"DEBUG: Asset Polling... Current Status: {status}")
                    if status == "AVAILABLE":
                        print("DEBUG: Asset is AVAILABLE and ready for posting.")
                        break
                else:
                    print(f"DEBUG: Asset check returned {check_response.status_code}: {check_response.text}")
            except Exception as e:
                print(f"DEBUG: Asset check error: {str(e)}")
            
            time.sleep(3)
            
        return asset_urn
