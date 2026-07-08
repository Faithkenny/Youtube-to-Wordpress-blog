"""
Test OpenAI API connection using the API key from .env file
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Get the API key
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    exit(1)

print(f"API Key found: {api_key[:10]}...{api_key[-4:]}")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

print("Connecting to OpenAI API...")

try:
    # Test the connection by listing available models
    models = client.models.list()
    print(f"✓ Successfully connected to OpenAI API")
    print(f"✓ Total models available: {len(models.data)}")
    
    # Show first few models
    print("\nAvailable models (first 5):")
    for i, model in enumerate(models.data[:5], 1):
        print(f"  {i}. {model.id}")
    
    # Test a simple completion
    print("\nTesting simple completion...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say 'Hello from OpenAI API!' in exactly those words."}
        ],
        max_tokens=50
    )
    
    print(f"✓ Completion successful")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"✗ Error connecting to OpenAI API: {str(e)}")
    exit(1)

print("\n✓ OpenAI API connection verified successfully!")
