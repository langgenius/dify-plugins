from collections.abc import Generator
from typing import Any, Dict, Optional, List
import requests
import json
import time
import re
from urllib.parse import urlparse
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class StructuredDataFeedsTool(Tool):
    """Intelligent BrightData tool that auto-selects appropriate data extractor based on request context"""

    # Complete tool configuration mapping - All 30+ BrightData tools
    TOOL_CONFIGS = {
        # ===== E-COMMERCE TOOLS =====
        'amazon_product': {
            'dataset_id': 'gd_l7q7dkf244hwjntr0',
            'url_patterns': [r'amazon\.[a-z]+/.*?/dp/', r'amazon\.[a-z]+/dp/'],
            'keywords': ['amazon product', 'amazon.com', 'amazon item'],
            'required_params': ['url'],
            'description': 'Amazon product data'
        },
        'amazon_product_reviews': {
            'dataset_id': 'gd_le8e811kzy4ggddlq',
            'url_patterns': [r'amazon\.[a-z]+/.*?/dp/', r'amazon\.[a-z]+/dp/'],
            'keywords': ['amazon review', 'amazon feedback', 'amazon rating'],
            'required_params': ['url'],
            'description': 'Amazon product reviews'
        },
        'amazon_product_search': {
            'dataset_id': 'gd_lwdb4vjm1ehb499uxs',
            'keywords': ['search amazon', 'amazon search', 'find on amazon'],
            'required_params': ['keyword', 'url'],
            'defaults': {'pages_to_search': '1'},
            'description': 'Amazon product search'
        },
        'walmart_product': {
            'dataset_id': 'gd_l95fol7l1ru6rlo116',
            'url_patterns': [r'walmart\.com/ip/'],
            'keywords': ['walmart product', 'walmart.com', 'walmart item'],
            'required_params': ['url'],
            'description': 'Walmart product data'
        },
        'walmart_seller': {
            'dataset_id': 'gd_m7ke48w81ocyu4hhz0',
            'url_patterns': [r'walmart\.com.*seller'],
            'keywords': ['walmart seller', 'walmart vendor'],
            'required_params': ['url'],
            'description': 'Walmart seller data'
        },
        'ebay_product': {
            'dataset_id': 'gd_ltr9mjt81n0zzdk1fb',
            'url_patterns': [r'ebay\.[a-z]+/itm/'],
            'keywords': ['ebay', 'ebay item', 'ebay listing'],
            'required_params': ['url'],
            'description': 'eBay product data'
        },
        'homedepot_products': {
            'dataset_id': 'gd_lmusivh019i7g97q2n',
            'url_patterns': [r'homedepot\.com/p/'],
            'keywords': ['home depot', 'homedepot'],
            'required_params': ['url'],
            'description': 'Home Depot product data'
        },
        'zara_products': {
            'dataset_id': 'gd_lct4vafw1tgx27d4o0',
            'url_patterns': [r'zara\.com'],
            'keywords': ['zara', 'zara product'],
            'required_params': ['url'],
            'description': 'Zara product data'
        },
        'etsy_products': {
            'dataset_id': 'gd_ltppk0jdv1jqz25mz',
            'url_patterns': [r'etsy\.com/listing/'],
            'keywords': ['etsy', 'etsy product', 'etsy listing'],
            'required_params': ['url'],
            'description': 'Etsy product data'
        },
        'bestbuy_products': {
            'dataset_id': 'gd_ltre1jqe1jfr7cccf',
            'url_patterns': [r'bestbuy\.com/site/'],
            'keywords': ['best buy', 'bestbuy'],
            'required_params': ['url'],
            'description': 'Best Buy product data'
        },
        
        # ===== SOCIAL MEDIA TOOLS - LINKEDIN =====
        'linkedin_person_profile': {
            'dataset_id': 'gd_l1viktl72bvl7bjuj0',
            'url_patterns': [r'linkedin\.com/in/'],
            'keywords': ['linkedin profile', 'linkedin person', 'linkedin user'],
            'required_params': ['url'],
            'description': 'LinkedIn person profile'
        },
        'linkedin_company_profile': {
            'dataset_id': 'gd_l1vikfnt1wgvvqz95w',
            'url_patterns': [r'linkedin\.com/company/'],
            'keywords': ['linkedin company', 'company linkedin'],
            'required_params': ['url'],
            'description': 'LinkedIn company profile'
        },
        'linkedin_job_listings': {
            'dataset_id': 'gd_lpfll7v5hcqtkxl6l',
            'url_patterns': [r'linkedin\.com/jobs/'],
            'keywords': ['linkedin jobs', 'linkedin job listing'],
            'required_params': ['url'],
            'description': 'LinkedIn job listings'
        },
        'linkedin_posts': {
            'dataset_id': 'gd_lyy3tktm25m4avu764',
            'url_patterns': [r'linkedin\.com/posts/', r'linkedin\.com/feed/'],
            'keywords': ['linkedin post', 'linkedin feed'],
            'required_params': ['url'],
            'description': 'LinkedIn posts'
        },
        'linkedin_people_search': {
            'dataset_id': 'gd_m8d03he47z8nwb5xc',
            'keywords': ['search linkedin person', 'find linkedin profile'],
            'required_params': ['url', 'first_name', 'last_name'],
            'description': 'LinkedIn people search'
        },
        
        # ===== BUSINESS DATA TOOLS =====
        'crunchbase_company': {
            'dataset_id': 'gd_l1vijqt9jfj7olije',
            'url_patterns': [r'crunchbase\.com/organization/'],
            'keywords': ['crunchbase', 'startup data', 'company funding'],
            'required_params': ['url'],
            'description': 'Crunchbase company data'
        },
        'zoominfo_company_profile': {
            'dataset_id': 'gd_m0ci4a4ivx3j5l6nx',
            'url_patterns': [r'zoominfo\.com/c/'],
            'keywords': ['zoominfo', 'company info', 'b2b data'],
            'required_params': ['url'],
            'description': 'ZoomInfo company profile'
        },
        'yahoo_finance_business': {
            'dataset_id': 'gd_lmrpz3vxmz972ghd7',
            'url_patterns': [r'finance\.yahoo\.com/quote/'],
            'keywords': ['yahoo finance', 'stock data', 'company financials'],
            'required_params': ['url'],
            'description': 'Yahoo Finance business data'
        },
        
        # ===== SOCIAL MEDIA TOOLS - INSTAGRAM =====
        'instagram_profiles': {
            'dataset_id': 'gd_l1vikfch901nx3by4',
            'url_patterns': [r'instagram\.com/[^/]+/?$'],
            'keywords': ['instagram profile', 'ig profile', 'insta user'],
            'required_params': ['url'],
            'description': 'Instagram profile data'
        },
        'instagram_posts': {
            'dataset_id': 'gd_lk5ns7kz21pck8jpis',
            'url_patterns': [r'instagram\.com/p/'],
            'keywords': ['instagram post', 'ig post', 'insta post'],
            'required_params': ['url'],
            'description': 'Instagram post data'
        },
        'instagram_reels': {
            'dataset_id': 'gd_lyclm20il4r5helnj',
            'url_patterns': [r'instagram\.com/reel/'],
            'keywords': ['instagram reel', 'ig reel', 'insta reel'],
            'required_params': ['url'],
            'description': 'Instagram reel data'
        },
        'instagram_comments': {
            'dataset_id': 'gd_ltppn085pokosxh13',
            'url_patterns': [r'instagram\.com/p/', r'instagram\.com/reel/'],
            'keywords': ['instagram comments', 'ig comments'],
            'required_params': ['url'],
            'description': 'Instagram comments'
        },
        
        # ===== SOCIAL MEDIA TOOLS - FACEBOOK =====
        'facebook_posts': {
            'dataset_id': 'gd_lyclm1571iy3mv57zw',
            'url_patterns': [r'facebook\.com/.*/posts/'],
            'keywords': ['facebook post', 'fb post'],
            'required_params': ['url'],
            'description': 'Facebook post data'
        },
        'facebook_marketplace_listings': {
            'dataset_id': 'gd_lvt9iwuh6fbcwmx1a',
            'url_patterns': [r'facebook\.com/marketplace/item/'],
            'keywords': ['facebook marketplace', 'fb marketplace'],
            'required_params': ['url'],
            'description': 'Facebook marketplace listing'
        },
        'facebook_company_reviews': {
            'dataset_id': 'gd_m0dtqpiu1mbcyc2g86',
            'keywords': ['facebook reviews', 'fb company reviews'],
            'required_params': ['url', 'num_of_reviews'],
            'description': 'Facebook company reviews'
        },
        'facebook_events': {
            'dataset_id': 'gd_m14sd0to1jz48ppm51',
            'url_patterns': [r'facebook\.com/events/'],
            'keywords': ['facebook event', 'fb event'],
            'required_params': ['url'],
            'description': 'Facebook events'
        },
        
        # ===== SOCIAL MEDIA TOOLS - TIKTOK =====
        'tiktok_profiles': {
            'dataset_id': 'gd_l1villgoiiidt09ci',
            'url_patterns': [r'tiktok\.com/@[^/]+/?$'],
            'keywords': ['tiktok profile', 'tiktok user'],
            'required_params': ['url'],
            'description': 'TikTok profile data'
        },
        'tiktok_posts': {
            'dataset_id': 'gd_lu702nij2f790tmv9h',
            'url_patterns': [r'tiktok\.com/.*/video/'],
            'keywords': ['tiktok video', 'tiktok post'],
            'required_params': ['url'],
            'description': 'TikTok post data'
        },
        'tiktok_shop': {
            'dataset_id': 'gd_m45m1u911dsa4274pi',
            'url_patterns': [r'tiktok\.com/.*/product/'],
            'keywords': ['tiktok shop', 'tiktok product'],
            'required_params': ['url'],
            'description': 'TikTok shop data'
        },
        'tiktok_comments': {
            'dataset_id': 'gd_lkf2st302ap89utw5k',
            'url_patterns': [r'tiktok\.com/.*/video/'],
            'keywords': ['tiktok comments'],
            'required_params': ['url'],
            'description': 'TikTok comments'
        },
        
        # ===== SOCIAL MEDIA TOOLS - OTHER =====
        'x_posts': {
            'dataset_id': 'gd_lwxkxvnf1cynvib9co',
            'url_patterns': [r'x\.com/.*/status/', r'twitter\.com/.*/status/'],
            'keywords': ['twitter post', 'tweet', 'x post'],
            'required_params': ['url'],
            'description': 'X (Twitter) post data'
        },
        'youtube_videos': {
            'dataset_id': 'gd_m5mbdl081229ln6t4a',
            'url_patterns': [r'youtube\.com/watch', r'youtu\.be/'],
            'keywords': ['youtube video', 'youtube'],
            'required_params': ['url'],
            'description': 'YouTube video data'
        },
        'youtube_profiles': {
            'dataset_id': 'gd_lk538t2k2p1k3oos71',
            'url_patterns': [r'youtube\.com/channel/', r'youtube\.com/c/', r'youtube\.com/@'],
            'keywords': ['youtube channel', 'youtube profile'],
            'required_params': ['url'],
            'description': 'YouTube channel data'
        },
        'youtube_comments': {
            'dataset_id': 'gd_lk9q0ew71spt1mxywf',
            'url_patterns': [r'youtube\.com/watch', r'youtu\.be/'],
            'keywords': ['youtube comments'],
            'required_params': ['url'],
            'defaults': {'num_of_comments': '10'},
            'description': 'YouTube comments'
        },
        'reddit_posts': {
            'dataset_id': 'gd_lvz8ah06191smkebj4',
            'url_patterns': [r'reddit\.com/r/.*/comments/'],
            'keywords': ['reddit post', 'reddit thread'],
            'required_params': ['url'],
            'description': 'Reddit post data'
        },
        
        # ===== OTHER TOOLS =====
        'google_maps_reviews': {
            'dataset_id': 'gd_luzfs1dn2oa0teb81',
            'url_patterns': [r'google\.com/maps/place/'],
            'keywords': ['google maps reviews', 'place reviews'],
            'required_params': ['url'],
            'defaults': {'days_limit': '3'},
            'description': 'Google Maps reviews'
        },
        'google_shopping': {
            'dataset_id': 'gd_ltppk50q18kdw67omz',
            'url_patterns': [r'shopping\.google\.com/product/'],
            'keywords': ['google shopping'],
            'required_params': ['url'],
            'description': 'Google Shopping data'
        },
        'google_play_store': {
            'dataset_id': 'gd_lsk382l8xei8vzm4u',
            'url_patterns': [r'play\.google\.com/store/apps/details'],
            'keywords': ['google play', 'android app'],
            'required_params': ['url'],
            'description': 'Google Play Store app data'
        },
        'apple_app_store': {
            'dataset_id': 'gd_lsk9ki3u2iishmwrui',
            'url_patterns': [r'apps\.apple\.com/.*/app/'],
            'keywords': ['app store', 'ios app', 'apple app'],
            'required_params': ['url'],
            'description': 'Apple App Store data'
        },
        'reuter_news': {
            'dataset_id': 'gd_lyptx9h74wtlvpnfu',
            'url_patterns': [r'reuters\.com/'],
            'keywords': ['reuters news', 'reuters article'],
            'required_params': ['url'],
            'description': 'Reuters news article'
        },
        'github_repository_file': {
            'dataset_id': 'gd_lyrexgxc24b3d4imjt',
            'url_patterns': [r'github\.com/.*/blob/'],
            'keywords': ['github file', 'github code'],
            'required_params': ['url'],
            'description': 'GitHub repository file'
        },
        'zillow_properties_listing': {
            'dataset_id': 'gd_lfqkr8wm13ixtbd8f5',
            'url_patterns': [r'zillow\.com/homedetails/'],
            'keywords': ['zillow', 'real estate', 'property listing'],
            'required_params': ['url'],
            'description': 'Zillow property listing'
        },
        'booking_hotel_listings': {
            'dataset_id': 'gd_m5mbdl081229ln6t4a',
            'url_patterns': [r'booking\.com/hotel/'],
            'keywords': ['booking.com', 'hotel listing', 'accommodation'],
            'required_params': ['url'],
            'description': 'Booking.com hotel listing'
        }
    }

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Main entry point for the smart data tool"""
        try:
            api_token = self.runtime.credentials["api_token"]
        except KeyError:
            raise Exception("Bright Data API token is required.")

        # Extract parameters
        request = tool_parameters.get("request", "").strip()
        url = tool_parameters.get("url", "").strip() if tool_parameters.get("url") else None
        additional_params_str = tool_parameters.get("additional_params", "")
        
        if not request and not url:
            raise Exception("Either 'request' description or 'url' must be provided.")

        # Parse additional parameters
        additional_params = {}
        if additional_params_str:
            try:
                additional_params = json.loads(additional_params_str)
            except json.JSONDecodeError:
                yield self.create_text_message("⚠️ Warning: Invalid JSON in additional_params, ignoring...")

        try:
            # Step 1: Determine which tool to use
            selected_tool = self._determine_tool(request, url)
            yield self.create_text_message(f"🔍 **Selected Tool**: {selected_tool}")
            yield self.create_text_message(f"📋 **Description**: {self.TOOL_CONFIGS[selected_tool]['description']}")
            
            # Step 2: Prepare parameters for the selected tool
            tool_params = self._prepare_tool_parameters(selected_tool, url, additional_params, request)
            
            # Step 3: Execute the data extraction
            result = self._execute_data_extraction(selected_tool, tool_params, api_token)
            
            yield self.create_text_message("✅ **Data extraction completed successfully!**")
            yield self.create_text_message(result)
            
        except Exception as e:
            # Smart error handling with fallback suggestions
            error_msg, fallback_suggestion = self._handle_smart_error(str(e), request, url)
            yield self.create_text_message(f"❌ **Error**: {error_msg}")
            if fallback_suggestion:
                yield self.create_text_message(f"💡 **Suggestion**: {fallback_suggestion}")
            raise Exception(error_msg)

    def _determine_tool(self, request: str, url: Optional[str] = None) -> str:
        """Smart tool selection based on URL patterns and request keywords"""
        
        # Priority 1: URL-based detection (most reliable)
        if url:
            for tool_name, config in self.TOOL_CONFIGS.items():
                for pattern in config.get('url_patterns', []):
                    if re.search(pattern, url, re.IGNORECASE):
                        return tool_name
        
        # Priority 2: Keyword-based detection from request
        if request:
            request_lower = request.lower()
            
            # Score each tool based on keyword matches
            tool_scores = {}
            for tool_name, config in self.TOOL_CONFIGS.items():
                score = 0
                for keyword in config.get('keywords', []):
                    if keyword in request_lower:
                        # Longer keywords get higher scores
                        score += len(keyword.split())
                
                if score > 0:
                    tool_scores[tool_name] = score
            
            # Return the highest scoring tool
            if tool_scores:
                return max(tool_scores, key=tool_scores.get)
        
        # Priority 3: Default fallback based on common patterns
        if url:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Simple domain mapping
            domain_mapping = {
                'amazon': 'amazon_product',
                'linkedin': 'linkedin_person_profile',
                'instagram': 'instagram_profiles',
                'youtube': 'youtube_videos',
                'reddit': 'reddit_posts',
                'crunchbase': 'crunchbase_company'
            }
            
            for domain_key, tool_name in domain_mapping.items():
                if domain_key in domain:
                    return tool_name
        
        # Ultimate fallback
        raise Exception(f"Could not determine appropriate tool for request: '{request}' and URL: '{url}'. Please be more specific or check the URL format.")

    def _prepare_tool_parameters(self, tool_name: str, url: Optional[str], additional_params: dict, request: str) -> dict:
        """Prepare parameters for the selected tool"""
        
        config = self.TOOL_CONFIGS[tool_name]
        params = {}
        
        # Add required parameters
        for param in config.get('required_params', []):
            if param == 'url' and url:
                params['url'] = url
            elif param == 'keyword' and not additional_params.get('keyword'):
                # Extract keyword from request for search tools
                if 'search' in tool_name or 'keyword' in config.get('required_params', []):
                    # Simple keyword extraction - in production, could be more sophisticated
                    params['keyword'] = request.replace('search for', '').replace('find', '').strip()
            elif param in additional_params:
                params[param] = additional_params[param]
        
        # Add default parameters
        defaults = config.get('defaults', {})
        if isinstance(defaults, dict):  # FIX: Check if defaults is a dict
            for param, default_value in defaults.items():
                if param not in params:
                    params[param] = default_value
        
        # Add any additional parameters that aren't already included
        if isinstance(additional_params, dict):  # FIX: Check if additional_params is a dict
            for key, value in additional_params.items():
                if key not in params:
                    params[key] = value
        
        return params

    def _execute_data_extraction(self, tool_name: str, params: dict, api_token: str) -> str:
        """Execute the data extraction using BrightData API"""
        
        config = self.TOOL_CONFIGS[tool_name]
        dataset_id = config['dataset_id']
        
        headers = {
            'user-agent': 'dify-plugin/1.0.0',
            'authorization': f'Bearer {api_token}',
        }
        
        # Step 1: Trigger data collection
        trigger_payload = [params]
        
        try:
            trigger_response = requests.post(
                'https://api.brightdata.com/datasets/v3/trigger',
                params={'dataset_id': dataset_id, 'include_errors': True},
                json=trigger_payload,
                headers=headers,
                timeout=30
            )
            
            if trigger_response.status_code != 200:
                try:
                    error_json = trigger_response.json()
                    if isinstance(error_json, dict):
                        error_msg = error_json.get('error', 'Unknown error')
                        if 'errors' in error_json:
                            error_details = error_json['errors']
                            error_msg += f" - Details: {error_details}"
                        raise Exception(f"BrightData API Error: {error_msg}")
                except json.JSONDecodeError:
                    pass
                
                raise Exception(f"API Error {trigger_response.status_code}: {trigger_response.text}")
            
            trigger_data = trigger_response.json()
            
            if not isinstance(trigger_data, dict):
                raise Exception('Invalid trigger response format')
            
            if not trigger_data.get('snapshot_id'):
                raise Exception('No snapshot ID returned from request')
            
            snapshot_id = trigger_data['snapshot_id']
            
            # Step 2: Poll for results
            return self._poll_for_results(snapshot_id, headers, tool_name)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network request failed: {str(e)}")

    def _poll_for_results(self, snapshot_id: str, headers: dict, tool_name: str) -> str:
        """Poll BrightData API for results with smart retry logic"""
        
        max_attempts = 600  # 10 minutes max
        attempts = 0
        
        while attempts < max_attempts:
            try:
                snapshot_response = requests.get(
                    f'https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}',
                    params={'format': 'json'},
                    headers=headers,
                    timeout=30
                )
                
                # Handle 202 (still processing) - this is normal
                if snapshot_response.status_code == 202:
                    attempts += 1
                    time.sleep(1)
                    continue
                
                if snapshot_response.status_code != 200:
                    raise Exception(f"Snapshot API error {snapshot_response.status_code}: {snapshot_response.text}")
                
                try:
                    snapshot_data = snapshot_response.json()
                    
                    # Handle different response formats gracefully
                    if isinstance(snapshot_data, list):
                        if len(snapshot_data) > 0:
                            if isinstance(snapshot_data[0], dict):
                                actual_data = snapshot_data[0]
                            else:
                                actual_data = {"data": snapshot_data, "status": "completed"}
                        else:
                            actual_data = {"data": [], "status": "completed", "message": "No data returned"}
                    elif isinstance(snapshot_data, dict):
                        actual_data = snapshot_data
                    else:
                        actual_data = {"data": snapshot_data, "status": "completed"}
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, return raw text
                    return f"## Raw Response Data\n\n**Tool Used**: `{tool_name}`\n**Response**: {snapshot_response.text}"
                
                # Check if still running
                status = None
                if isinstance(actual_data, dict):
                    status = actual_data.get('status')
                
                if status == 'running':
                    attempts += 1
                    time.sleep(1)
                    continue
                
                # Data is ready - format and return
                return self._format_extracted_data(actual_data, tool_name)
                
            except requests.exceptions.RequestException as e:
                attempts += 1
                time.sleep(1)
                if attempts >= max_attempts:
                    raise Exception(f"Request failed after {max_attempts} attempts: {str(e)}")
        
        raise Exception(f"Timeout after {max_attempts} seconds waiting for data")

    def _format_extracted_data(self, data, tool_name: str) -> str:
        """Format the extracted data in a user-friendly way"""
        
        try:
            # Handle different data types
            if isinstance(data, dict):
                formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
                status = data.get('status', 'completed')
            elif isinstance(data, list):
                formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
                status = 'completed'
            else:
                formatted_data = str(data)
                status = 'completed'
            
            # Add context about what was extracted
            result = f"## {tool_name.replace('_', ' ').title()} Data\n\n"
            result += f"**Tool Used**: `{tool_name}`\n"
            result += f"**Status**: {status}\n\n"
            result += "### Extracted Data:\n"
            
            # Format based on data type
            if isinstance(data, (dict, list)):
                result += f"```json\n{formatted_data}\n```"
            else:
                result += f"```\n{formatted_data}\n```"
            
            return result
            
        except Exception as e:
            return f"## Extracted Data\n\n**Tool Used**: `{tool_name}`\n**Raw Data**: {str(data)}\n**Error**: {str(e)}"

    def _handle_smart_error(self, error_msg: str, request: str, url: Optional[str]) -> tuple[str, Optional[str]]:
        """Provide intelligent error handling with suggestions"""
        
        suggestion = None
        
        if "Could not determine appropriate tool" in error_msg:
            suggestion = "Try being more specific in your request. Examples: 'Get Amazon product info', 'Extract LinkedIn profile', 'Find company data from Crunchbase'"
        
        elif "Invalid" in error_msg and url:
            parsed = urlparse(url) if url else None
            if parsed and parsed.netloc:
                domain = parsed.netloc.lower()
                if 'amazon' in domain:
                    suggestion = "Make sure the Amazon URL contains '/dp/' or '/gp/product/' for product pages"
                elif 'linkedin' in domain:
                    suggestion = "Use direct LinkedIn profile URLs like 'linkedin.com/in/username' or 'linkedin.com/company/companyname'"
                elif 'instagram' in domain:
                    suggestion = "Use Instagram profile URLs like 'instagram.com/username' or post URLs like 'instagram.com/p/postid'"
        
        elif "API error" in error_msg:
            suggestion = "This might be a temporary API issue. Try again in a few moments, or check if your BrightData API token is valid and has sufficient credits."
        
        return error_msg, suggestion