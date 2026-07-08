"""
Summarize YouTube transcript using OpenAI ChatGPT
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from youtube_transcript import get_transcript

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# YouTube URL to summarize
url = 'https://youtu.be/JU9z3RRzC_8?si=1ZLVSG5_KSRc1izG'

print("Fetching transcript...")
result = get_transcript(url)

if not result['success']:
    print(f"Error fetching transcript: {result['error']}")
    exit(1)

transcript = result['transcript']
print(f"✓ Transcript fetched: {len(transcript)} characters")
print(f"Video ID: {result['video_id']}")

print("\nSending to ChatGPT for summarization...")

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes video transcripts into clear, concise bullet points."
            },
            {
                "role": "user",
                "content": f"""Please summarize the following YouTube transcript into 5-7 key bullet points. Focus on clarity and conciseness. Format as markdown bullets.

Transcript:
{transcript}"""
            }
        ],
        max_tokens=1000,
        temperature=0.7
    )
    
    summary = response.choices[0].message.content
    print("\n" + "="*50)
    print("TRANSCRIPT SUMMARY")
    print("="*50)
    print(summary)
    print("="*50)
    
except Exception as e:
    print(f"Error generating summary: {str(e)}")
    exit(1)

print("\n✓ Summary generated successfully!")
