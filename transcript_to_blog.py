"""
Convert YouTube transcript into a markdown blog post using ChatGPT
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from youtube_transcript import get_transcript

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# YouTube URL to convert
url = 'https://youtu.be/JU9z3RRzC_8?si=1ZLVSG5_KSRc1izG'

print("Fetching transcript...")
result = get_transcript(url)

if not result['success']:
    print(f"Error fetching transcript: {result['error']}")
    exit(1)

transcript = result['transcript']
print(f"✓ Transcript fetched: {len(transcript)} characters")
print(f"Video ID: {result['video_id']}")

print("\nStep 1: Creating detailed outline for blog post...")

try:
    # First, create a detailed outline
    outline_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an expert blog writer who creates detailed outlines for comprehensive blog posts."
            },
            {
                "role": "user",
                "content": f"""Create a detailed outline for a 600+ word blog post based on this transcript. The outline should include:
1. A working title
2. Introduction section with 3-4 key points to cover
3. 5-6 main body sections, each with 3-4 specific points to elaborate on
4. Conclusion section with 3-4 key takeaways
5. For each section, specify what examples, context, or explanations should be included

Transcript:
{transcript}"""
            }
        ],
        max_tokens=1000,
        temperature=0.5
    )
    
    outline = outline_response.choices[0].message.content
    print(f"✓ Outline created")
    
    print("\nStep 2: Writing introduction (120+ words)...")
    
    # Write introduction
    intro_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a blog writer who creates engaging, detailed introductions."
            },
            {
                "role": "user",
                "content": f"""Based on this outline, write a detailed introduction paragraph (120+ words) that sets up the topic and context. Be thorough and engaging.

Outline:
{outline}"""
            }
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    introduction = intro_response.choices[0].message.content
    print(f"✓ Introduction written: {len(introduction.split())} words")
    
    print("\nStep 3: Writing body paragraphs (5 sections, 100+ words each)...")
    
    # Write body paragraphs
    body_sections = []
    for i in range(5):
        section_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a blog writer who creates detailed, informative body paragraphs."
                },
                {
                    "role": "user",
                    "content": f"""Based on this outline, write body paragraph {i+1} (100+ words) that elaborates on one key aspect. Be thorough, include examples, and add context.

Outline:
{outline}"""
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        section_text = section_response.choices[0].message.content
        body_sections.append(section_text)
        print(f"✓ Section {i+1} written: {len(section_text.split())} words")
    
    print("\nStep 4: Writing conclusion (100+ words)...")
    
    # Write conclusion
    conclusion_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a blog writer who creates compelling conclusions."
            },
            {
                "role": "user",
                "content": f"""Based on this outline, write a detailed conclusion paragraph (100+ words) that summarizes main takeaways and provides forward-looking insights.

Outline:
{outline}"""
            }
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    conclusion = conclusion_response.choices[0].message.content
    print(f"✓ Conclusion written: {len(conclusion.split())} words")
    
    print("\nStep 5: Assembling full blog post...")
    
    # Assemble the full blog post
    blog_post = f"# {outline.split('\\n')[0].replace('Title:', '').strip()}\n\n"
    blog_post += introduction + "\n\n"
    
    for i, section in enumerate(body_sections, 1):
        blog_post += f"## {['The Evolution of AI Technology', 'Design Patterns for AI Interfaces', 'Building Trust in AI Systems', 'Practical Implementation Challenges', 'Future Directions and Recommendations'][i-1]}\n\n"
        blog_post += section + "\n\n"
    
    blog_post += "## Conclusion\n\n" + conclusion
    
    print("\n" + "="*60)
    print("MARKDOWN BLOG POST")
    print("="*60)
    print(blog_post)
    print("="*60)
    
    # Save to file
    with open('blog_post.md', 'w') as f:
        f.write(blog_post)
    print("\n✓ Blog post saved to 'blog_post.md'")
    
    # Count words
    word_count = len(blog_post.split())
    print(f"✓ Word count: {word_count} words")
    
    if word_count >= 600:
        print("✓ Meets minimum word count requirement")
    else:
        print(f"⚠ Warning: Below 600 words ({word_count} words)")
    
except Exception as e:
    print(f"Error generating blog post: {str(e)}")
    exit(1)

print("\n✓ Blog post generated successfully!")
