"""
Publish markdown blog post to WordPress using REST API
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

# Read the markdown blog post
try:
    with open('blog_post.md', 'r') as f:
        markdown_content = f.read()
    print(f"✓ Read blog post from blog_post.md ({len(markdown_content)} characters)")
except FileNotFoundError:
    print("Error: blog_post.md file not found")
    exit(1)

# WordPress REST API endpoint
api_url = f"{wordpress_url.rstrip('/')}/wp-json/wp/v2/posts"

# Create Basic Auth header
auth_string = f"{username}:{app_password}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
headers = {
    'Authorization': f'Basic {auth_b64}',
    'Content-Type': 'application/json'
}

# Extract title from markdown (first line starting with #)
title = "Blog Post from YouTube Transcript"
lines = markdown_content.split('\n')
for line in lines:
    if line.startswith('# '):
        title = line.replace('# ', '').strip()
        break

print(f"\nPublishing to WordPress...")
print(f"API URL: {api_url}")
print(f"Title: {title}")
print(f"Status: draft")

# Prepare post data
post_data = {
    'title': title,
    'content': markdown_content,
    'status': 'draft',
    'content_format': 'markdown'  # Try to use markdown format
}

try:
    response = requests.post(api_url, headers=headers, json=post_data)
    
    if response.status_code == 201:
        post_data = response.json()
        print("\n" + "=" * 50)
        print("✓ Successfully published blog post as draft!")
        print("=" * 50)
        print(f"Post ID: {post_data.get('id')}")
        print(f"Title: {post_data.get('title', {}).get('rendered')}")
        print(f"Status: {post_data.get('status')}")
        print(f"Link: {post_data.get('link')}")
        print(f"Draft URL: {post_data.get('link')}?preview=true")
        print("=" * 50)
    elif response.status_code == 401:
        print("✗ Authentication failed - Invalid credentials")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    elif response.status_code == 403:
        print("✗ Forbidden - Insufficient permissions")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    else:
        print(f"✗ Failed to publish post")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"✗ Error publishing to WordPress: {str(e)}")
    exit(1)

print("\n✓ WordPress publishing completed!")
