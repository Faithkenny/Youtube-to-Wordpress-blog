"""
Test WordPress API connection using application password authentication
"""

import os
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get WordPress credentials from environment variables
wordpress_url = os.getenv('WORDPRESS_URL')
username = os.getenv('WORDPRESS_USERNAME')
app_password = os.getenv('WORDPRESS_APP_PASSWORD')

if not all([wordpress_url, username, app_password]):
    print("Error: WordPress credentials not found in .env file")
    print("Required: WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD")
    exit(1)

print("WordPress API Connection Test")
print("=" * 50)
print(f"URL: {wordpress_url}")
print(f"Username: {username}")
print(f"App Password: {'*' * len(app_password)}")
print()

# This appears to be a WordPress.com hosted site with custom domain
# Try standard WordPress REST API first (works for most WordPress installations)
api_base_standard = f"{wordpress_url.rstrip('/')}/wp-json/wp/v2"

# Also try WordPress.com public API
site_name = wordpress_url.rstrip('/').replace('https://', '').replace('http://', '')
print(f"Site name extracted: {site_name}")
api_base_wpcom = f"https://public-api.wordpress.com/rest/v1.3/sites/{site_name}"

# Create Basic Auth header
auth_string = f"{username}:{app_password}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
headers = {
    'Authorization': f'Basic {auth_b64}',
    'Content-Type': 'application/json'
}

print("Testing connection to WordPress REST API...")
print(f"Standard API: {api_base_standard}")
print(f"WordPress.com API: {api_base_wpcom}")

# Try both API endpoints
api_base = None
for api_name, api_url in [("Standard", api_base_standard), ("WordPress.com", api_base_wpcom)]:
    print(f"\nTrying {api_name} API...")
    try:
        response = requests.get(f"{api_url}")
        
        if response.status_code == 200:
            site_data = response.json()
            print(f"✓ Successfully connected to WordPress API ({api_name})")
            print(f"✓ Site ID: {site_data.get('ID')}")
            print(f"✓ Site Name: {site_data.get('name')}")
            print(f"✓ Site Description: {site_data.get('description')}")
            print(f"✓ Site URL: {site_data.get('URL')}")
            
            # Now try with authentication
            print(f"\nTesting authentication with {api_name}...")
            auth_response = requests.get(f"{api_url}", headers=headers)
            if auth_response.status_code == 200:
                print("✓ Authentication successful")
                api_base = api_url  # Use this API version for subsequent calls
                break
            else:
                print(f"⚠ Authentication returned status: {auth_response.status_code}")
        elif response.status_code == 404:
            print(f"✗ {api_name} API - Site not found")
        else:
            print(f"✗ {api_name} API - Status: {response.status_code}")
    except Exception as e:
        print(f"✗ {api_name} API - Error: {str(e)}")

if not api_base:
    print("\n✗ All API endpoints failed")
    exit(1)

# Test getting posts
print("\nTesting posts endpoint...")
try:
    response = requests.get(f"{api_base}/posts", headers=headers, params={'per_page': 5})
    
    if response.status_code == 200:
        posts = response.json()
        print(f"✓ Successfully retrieved {len(posts)} recent posts")
        for i, post in enumerate(posts, 1):
            print(f"  {i}. {post.get('title', {}).get('rendered', 'Untitled')} (ID: {post.get('id')})")
    else:
        print(f"✗ Failed to retrieve posts")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"✗ Error retrieving posts: {str(e)}")

print("\n" + "=" * 50)
print("WordPress API connection test completed!")
