from typing import List, Dict, Any
from ytmusicapi import YTMusic

class PlaylistManager:
    def __init__(self, ytmusic: YTMusic):
        self.ytmusic = ytmusic

    def create_playlist_batch(self, title: str, description: str, queries: List[str]) -> Dict[str, Any]:
        """
        Creates a playlist and adds songs found by searching for each query.
        Returns a summary of the operation.
        """
        # Create playlist first
        playlist_id = self.ytmusic.create_playlist(title=title, description=description)
        if isinstance(playlist_id, dict):
            # Handle error case or unexpected return
            raise RuntimeError(f"Failed to create playlist: {playlist_id}")
        
        results = []
        video_ids = []
        
        for query in queries:
            search_results = self.ytmusic.search(query, filter="songs", limit=1)
            if search_results:
                best_match = search_results[0]
                video_ids.append(best_match['videoId'])
                results.append({
                    "query": query,
                    "found": True,
                    "title": best_match.get('title'),
                    "artist": ", ".join(a['name'] for a in best_match.get('artists', [])),
                    "videoId": best_match['videoId']
                })
            else:
                results.append({
                    "query": query,
                    "found": False
                })
        
        # Add to playlist
        if video_ids:
            self.ytmusic.add_playlist_items(playlist_id, video_ids)
            
        return {
            "playlist_id": playlist_id,
            "playlist_url": f"https://music.youtube.com/playlist?list={playlist_id}",
            "track_count": len(video_ids),
            "details": results
        }
