"""
YouTube Transcript Extractor

This module provides functionality to extract transcripts from YouTube videos
using the youtube-transcript-api package.
"""

import re
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


class YouTubeTranscriptExtractor:
    """A class to extract transcripts from YouTube videos."""
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract the video ID from a YouTube URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID string or None if not found
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def get_transcript(url: str, language: str = 'en') -> dict:
        """
        Get the full transcript from a YouTube video.
        
        Args:
            url: YouTube video URL or video ID
            language: Preferred language code (default: 'en')
            
        Returns:
            Dictionary with keys:
                - 'success': bool indicating if extraction was successful
                - 'transcript': str containing the full transcript text
                - 'video_id': str the video ID
                - 'error': str error message if unsuccessful
        """
        result = {
            'success': False,
            'transcript': '',
            'video_id': '',
            'error': None
        }
        
        # Extract video ID
        video_id = YouTubeTranscriptExtractor.extract_video_id(url)
        if not video_id:
            result['error'] = 'Invalid YouTube URL or video ID'
            return result
        
        result['video_id'] = video_id
        
        try:
            # Get transcript list
            transcript_list = YouTubeTranscriptApi().fetch(video_id)
            
            # Combine all transcript segments into full text
            full_transcript = ' '.join([segment.text for segment in transcript_list])
            
            result['transcript'] = full_transcript
            result['success'] = True
            
        except TranscriptsDisabled:
            result['error'] = 'Transcripts are disabled for this video'
        except NoTranscriptFound:
            result['error'] = 'No transcript found for this video'
        except Exception as e:
            result['error'] = f'An error occurred: {str(e)}'
        
        return result
    
    @staticmethod
    def get_transcript_with_timestamps(url: str, language: str = 'en') -> dict:
        """
        Get transcript with timestamps from a YouTube video.
        
        Args:
            url: YouTube video URL or video ID
            language: Preferred language code (default: 'en')
            
        Returns:
            Dictionary with keys:
                - 'success': bool indicating if extraction was successful
                - 'transcript': list of dicts with 'text', 'start', 'duration'
                - 'video_id': str the video ID
                - 'error': str error message if unsuccessful
        """
        result = {
            'success': False,
            'transcript': [],
            'video_id': '',
            'error': None
        }
        
        # Extract video ID
        video_id = YouTubeTranscriptExtractor.extract_video_id(url)
        if not video_id:
            result['error'] = 'Invalid YouTube URL or video ID'
            return result
        
        result['video_id'] = video_id
        
        try:
            # Get transcript list with timestamps
            transcript_list = YouTubeTranscriptApi().fetch(video_id)
            
            result['transcript'] = transcript_list
            result['success'] = True
            
        except TranscriptsDisabled:
            result['error'] = 'Transcripts are disabled for this video'
        except NoTranscriptFound:
            result['error'] = 'No transcript found for this video'
        except Exception as e:
            result['error'] = f'An error occurred: {str(e)}'
        
        return result


def get_transcript(url: str, language: str = 'en') -> dict:
    """
    Convenience function to get transcript from a YouTube video.
    
    Args:
        url: YouTube video URL or video ID
        language: Preferred language code (default: 'en')
        
    Returns:
        Dictionary with transcript data
    """
    return YouTubeTranscriptExtractor.get_transcript(url, language)


def get_transcript_with_timestamps(url: str, language: str = 'en') -> dict:
    """
    Convenience function to get transcript with timestamps from a YouTube video.
    
    Args:
        url: YouTube video URL or video ID
        language: Preferred language code (default: 'en')
        
    Returns:
        Dictionary with transcript data including timestamps
    """
    return YouTubeTranscriptExtractor.get_transcript_with_timestamps(url, language)


if __name__ == '__main__':
    # Example usage
    test_url = input("Enter YouTube URL: ")
    
    print("\n--- Full Transcript ---")
    result = get_transcript(test_url)
    
    if result['success']:
        print(f"Video ID: {result['video_id']}")
        print(f"Transcript:\n{result['transcript']}")
    else:
        print(f"Error: {result['error']}")
    
    print("\n--- Transcript with Timestamps ---")
    result_timestamps = get_transcript_with_timestamps(test_url)
    
    if result_timestamps['success']:
        print(f"Video ID: {result_timestamps['video_id']}")
        print(f"Segments: {len(result_timestamps['transcript'])}")
        for segment in result_timestamps['transcript'][:5]:  # Show first 5 segments
            print(f"[{segment['start']:.2f}s] {segment['text']}")
    else:
        print(f"Error: {result_timestamps['error']}")
