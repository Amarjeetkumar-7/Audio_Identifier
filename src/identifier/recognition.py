from shazamio import Shazam
import asyncio


class MusicIdentifier:
    """Identifies music using Shazamio."""

    def __init__(self):
        self.shazam = Shazam()

    async def identify_clip(self, file_path: str):
        try:
            out = await self.shazam.recognize_song(file_path)
            return self._parse_response(out)
        except Exception as e:
            return {"error": str(e)}

    def _parse_response(self, result):
        if not result or 'track' not in result:
            return {"error": "No match found"}

        track = result['track']

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

        if not links:
            shazam_url = track.get('url') or track.get('share', {}).get('href')
            if shazam_url:
                links['shazam'] = shazam_url

        # Extract album from sections metadata
        album = 'Unknown'
        for section in track.get('sections', []):
            for meta in section.get('metadata', []):
                if meta.get('title', '').lower() == 'album':
                    album = meta.get('text', 'Unknown')
                    break

        # Extract year from sections metadata
        year = 'Unknown'
        for section in track.get('sections', []):
            for meta in section.get('metadata', []):
                if meta.get('title', '').lower() in ['released', 'year']:
                    year = meta.get('text', 'Unknown')
                    break

        return {
            "title":     track.get('title',    'Unknown'),
            "artist":    track.get('subtitle', 'Unknown'),
            "album":     album,
            "year":      year,
            "links":     links,
            "shazam_id": track.get('key')
        }
