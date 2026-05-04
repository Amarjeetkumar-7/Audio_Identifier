from shazamio import Shazam
import asyncio

class MusicIdentifier:
    """Module to identify music using Shazamio (No token required)."""
    
    def __init__(self):
        self.shazam = Shazam()

    async def identify_clip(self, file_path: str):
        """
        Sends the audio file to Shazam and returns metadata.
        Shazamio handles the fingerprinting locally before sending.
        """
        try:
            # The recognize method accepts the file path directly
            out = await self.shazam.recognize(file_path)
            return self._parse_response(out)
        except Exception as e:
            return {"error": str(e)}

    def _parse_response(self, result):
        """Extracts title, artist, and streaming links."""
        if not result or 'track' not in result:
            return {"error": "No match found"}

        track = result['track']
        
        # Extract streaming links from hub providers
        links = {}
        hub = track.get('hub', {})
        providers = hub.get('providers', [])
        for provider in providers:
            provider_type = provider.get('type', '').lower()
            actions = provider.get('actions', [])
            if actions:
                url = actions[0].get('uri') or actions[0].get('url')
                if provider_type == 'youtube':
                    links['youtube'] = url
        
        # Fallback to Shazam URL if no YouTube link
        if not links:
            shazam_url = track.get('url') or track.get('share', {}).get('href')
            if shazam_url:
                links['shazam'] = shazam_url

        return {
            "title": track.get('title'),
            "artist": track.get('subtitle'),
            "links": links,
            "shazam_id": track.get('key')
        }
    