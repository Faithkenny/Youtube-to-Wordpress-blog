"""
Flask web app for YouTube to WordPress blog post automation
"""

import os
import base64
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from openai import OpenAI
from youtube_transcript import get_transcript

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# WordPress credentials
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_USERNAME = os.getenv('WORDPRESS_USERNAME')
WORDPRESS_APP_PASSWORD = os.getenv('WORDPRESS_APP_PASSWORD')


def extract_transcript(url):
    """Extract transcript from YouTube URL"""
    result = get_transcript(url)
    if result['success']:
        return result['transcript'], None
    return None, result['error']


def generate_summary(transcript):
    """Generate summary using ChatGPT"""
    try:
        response = openai_client.chat.completions.create(
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
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)


def generate_blog_post(transcript):
    """Generate blog post using ChatGPT"""
    try:
        # Step 1: Create detailed outline
        outline_response = openai_client.chat.completions.create(
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
        
        # Step 2: Write introduction
        intro_response = openai_client.chat.completions.create(
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
        
        # Step 3: Write body paragraphs
        body_sections = []
        for i in range(5):
            section_response = openai_client.chat.completions.create(
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
        
        # Step 4: Write conclusion
        conclusion_response = openai_client.chat.completions.create(
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
        
        # Step 5: Assemble full blog post
        # Extract title from outline
        title = "Blog Post from YouTube Transcript"
        for line in outline.split('\n'):
            if line.lower().startswith('title:'):
                title = line.replace('Title:', '').replace('title:', '').strip()
                break
        
        blog_post = f"# {title}\n\n"
        blog_post += introduction + "\n\n"
        
        section_titles = [
            "The Evolution of AI Technology",
            "Design Patterns for AI Interfaces", 
            "Building Trust in AI Systems",
            "Practical Implementation Challenges",
            "Future Directions and Recommendations"
        ]
        
        for i, section in enumerate(body_sections, 1):
            blog_post += f"## {section_titles[i-1]}\n\n"
            blog_post += section + "\n\n"
        
        blog_post += "## Conclusion\n\n" + conclusion
        
        return blog_post, None
        
    except Exception as e:
        return None, str(e)


def publish_to_wordpress(markdown_content):
    """Publish blog post to WordPress as draft"""
    try:
        api_url = f"{WORDPRESS_URL.rstrip('/')}/wp-json/wp/v2/posts"
        
        # Create Basic Auth header
        auth_string = f"{WORDPRESS_USERNAME}:{WORDPRESS_APP_PASSWORD}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json'
        }
        
        # Extract title from markdown
        title = "Blog Post from YouTube Transcript"
        lines = markdown_content.split('\n')
        for line in lines:
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                break
        
        # Prepare post data
        post_data = {
            'title': title,
            'content': markdown_content,
            'status': 'draft',
            'content_format': 'markdown'
        }
        
        response = requests.post(api_url, headers=headers, json=post_data)
        
        if response.status_code == 201:
            post_data = response.json()
            return {
                'success': True,
                'post_id': post_data.get('id'),
                'title': post_data.get('title', {}).get('rendered'),
                'link': post_data.get('link'),
                'draft_url': f"{post_data.get('link')}?preview=true"
            }, None
        else:
            return None, f"WordPress API error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, str(e)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    youtube_url = request.form.get('youtube_url')
    
    if not youtube_url:
        flash('Please enter a YouTube URL', 'error')
        return redirect(url_for('index'))
    
    # Step 1: Extract transcript
    flash('Extracting transcript from YouTube...', 'info')
    transcript, error = extract_transcript(youtube_url)
    if error:
        flash(f'Error extracting transcript: {error}', 'error')
        return redirect(url_for('index'))
    
    flash(f'✓ Transcript extracted ({len(transcript)} characters)', 'success')
    
    # Step 2: Generate summary
    flash('Generating summary with ChatGPT...', 'info')
    summary, error = generate_summary(transcript)
    if error:
        flash(f'Error generating summary: {error}', 'error')
        return redirect(url_for('index'))
    
    flash('✓ Summary generated', 'success')
    
    # Step 3: Generate blog post
    flash('Generating blog post with ChatGPT...', 'info')
    blog_post, error = generate_blog_post(transcript)
    if error:
        flash(f'Error generating blog post: {error}', 'error')
        return redirect(url_for('index'))
    
    flash(f'✓ Blog post generated ({len(blog_post)} characters)', 'success')
    
    # Step 4: Publish to WordPress
    flash('Publishing to WordPress as draft...', 'info')
    result, error = publish_to_wordpress(blog_post)
    if error:
        flash(f'Error publishing to WordPress: {error}', 'error')
        return redirect(url_for('index'))
    
    flash('✓ Blog post published as draft!', 'success')
    
    return render_template('success.html', 
                         post_id=result['post_id'],
                         title=result['title'],
                         link=result['link'],
                         draft_url=result['draft_url'],
                         summary=summary)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
