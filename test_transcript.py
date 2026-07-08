from youtube_transcript import get_transcript, get_transcript_with_timestamps

url = 'https://youtu.be/JU9z3RRzC_8?si=1ZLVSG5_KSRc1izG'

print("Testing transcript extraction...")
print(f"URL: {url}\n")

# Get transcript with timestamps
result_timestamps = get_transcript_with_timestamps(url)

if result_timestamps['success']:
    print(f"✓ Successfully extracted transcript from video ID: {result_timestamps['video_id']}")
    print(f"Total segments: {len(result_timestamps['transcript'])}")
    
    print(f"\n--- First 3 transcript segments ---")
    for i, segment in enumerate(result_timestamps['transcript'][:3], 1):
        print(f"{i}. [{segment.start:.2f}s] {segment.text}")
else:
    print(f"✗ Error: {result_timestamps['error']}")
