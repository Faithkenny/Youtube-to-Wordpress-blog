from youtube_transcript import YouTubeTranscriptExtractor

# Test URL extraction without network calls
test_urls = [
    'https://youtu.be/JU9z3RRzC_8?si=1ZLVSG5_KSRc1izG',
    'https://www.youtube.com/watch?v=JU9z3RRzC_8',
    'https://youtube.com/embed/JU9z3RRzC_8',
    'https://youtube.com/shorts/JU9z3RRzC_8',
    'https://youtube.com/v/JU9z3RRzC_8',
    'JU9z3RRzC_8',
    'invalid-url'
]

print("Testing URL extraction logic:")
print("-" * 50)

for url in test_urls:
    video_id = YouTubeTranscriptExtractor.extract_video_id(url)
    status = "✓" if video_id == "JU9z3RRzC_8" else "✗"
    print(f"{status} {url[:50]:<50} -> {video_id or 'None'}")
