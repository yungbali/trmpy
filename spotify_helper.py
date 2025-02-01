import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import time
from typing import Dict, List, Optional
import socket
import requests

load_dotenv()

LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')

class SpotifyAnalyzer:
    def __init__(self):
        try:
            # Initialize with client credentials for public data only
            credentials = SpotifyClientCredentials(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
            )
            self.sp = spotipy.Spotify(client_credentials_manager=credentials)
            
        except Exception as e:
            print(f"Spotify initialization error: {e}")
            raise

    def _find_free_port(self):
        """Find a free port to use for the OAuth callback"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    def authenticate(self):
        """Authenticate user and return auth URL"""
        try:
            # Get the auth URL
            auth_url = self.auth_manager.get_authorize_url()
            return auth_url
        except Exception as e:
            print(f"Error getting auth URL: {e}")
            return None

    def validate_token(self):
        """Check if current token is valid"""
        try:
            return self.sp.current_user() is not None
        except:
            return False

    def get_current_user(self):
        """Get current user's profile"""
        try:
            return self.sp.current_user()
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None

    def get_top_tracks(self, time_range='short_term', limit=25):
        """Get user's top tracks"""
        try:
            results = self.sp.current_user_top_tracks(
                limit=limit,
                offset=0,
                time_range=time_range
            )
            
            tracks = []
            for item in results['items']:
                track_data = {
                    'id': item['id'],
                    'name': item['name'],
                    'artist': item['artists'][0]['name'],
                    'popularity': item['popularity'],
                    'preview_url': item['preview_url'],
                    'external_url': item['external_urls']['spotify']
                }
                tracks.append(track_data)
                
            return tracks
            
        except Exception as e:
            print(f"Error getting top tracks: {e}")
            return None

    def get_track_analysis(self, track_url):
        """Get detailed track analysis including audio features, segments, and lyrics"""
        try:
            track_id = self.extract_track_id(track_url)
            if not track_id:
                return None

            # Get audio analysis
            audio_analysis = self.sp.audio_analysis(track_id)
            
            # Get audio features
            audio_features = self.sp.audio_features([track_id])[0]
            
            # Get track metadata
            track_info = self.sp.track(track_id)
            
            # Get first 30 seconds of segments
            segments_30s = [
                segment for segment in audio_analysis['segments']
                if segment['start'] < 30.0
            ]
            
            # Extract key musical features from the first 30 seconds
            analysis = {
                'track_info': {
                    'name': track_info['name'],
                    'artist': track_info['artists'][0]['name'],
                    'duration': track_info['duration_ms'] / 1000,  # convert to seconds
                    'popularity': track_info['popularity']
                },
                'audio_features': {
                    'tempo': audio_features['tempo'],
                    'key': audio_features['key'],
                    'mode': audio_features['mode'],
                    'time_signature': audio_features['time_signature'],
                    'danceability': audio_features['danceability'],
                    'energy': audio_features['energy'],
                    'valence': audio_features['valence'],
                    'instrumentalness': audio_features['instrumentalness']
                },
                'first_30s_analysis': {
                    'average_loudness': sum(s['loudness_max'] for s in segments_30s) / len(segments_30s),
                    'segment_count': len(segments_30s),
                    'pitch_variety': self._analyze_pitch_variety(segments_30s),
                    'timbre_variety': self._analyze_timbre_variety(segments_30s)
                }
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing track: {str(e)}")
            return None

    def _analyze_pitch_variety(self, segments):
        """Analyze pitch variety in segments"""
        if not segments:
            return None
            
        # Calculate average pitches across segments
        pitch_sums = [sum(segment['pitches']) for segment in segments]
        return {
            'max': max(pitch_sums),
            'min': min(pitch_sums),
            'average': sum(pitch_sums) / len(pitch_sums)
        }

    def _analyze_timbre_variety(self, segments):
        """Analyze timbre variety in segments"""
        if not segments:
            return None
            
        # Calculate average timbre across segments
        timbre_sums = [sum(segment['timbre']) for segment in segments]
        return {
            'max': max(timbre_sums),
            'min': min(timbre_sums),
            'average': sum(timbre_sums) / len(timbre_sums)
        }

    def extract_track_id(self, spotify_url):
        """Extract track ID from Spotify URL"""
        try:
            if 'track/' in spotify_url:
                return spotify_url.split('track/')[1].split('?')[0]
            return None
        except Exception as e:
            print(f"Error extracting track ID: {str(e)}")
            return None

    def analyze_track(self, track_id):
        """Comprehensive track analysis combining basic info, audio features, and audio analysis"""
        try:
            # Get basic track info
            track_info = self.sp.track(track_id)
            
            # Get audio features
            features = self.sp.audio_features(track_id)[0]
            
            # Get detailed audio analysis
            analysis = self.sp.audio_analysis(track_id)
            
            # Extract first 30 seconds segments
            segments_30s = [
                segment for segment in analysis['segments'] 
                if segment['start'] < 30.0
            ]
            
            return {
                'basic_info': {
                    'name': track_info['name'],
                    'artist': track_info['artists'][0]['name'],
                    'popularity': track_info['popularity'],
                    'duration_ms': track_info['duration_ms']
                },
                'audio_features': {
                    'danceability': features['danceability'],
                    'energy': features['energy'],
                    'key': features['key'],
                    'loudness': features['loudness'],
                    'mode': features['mode'],
                    'speechiness': features['speechiness'],
                    'acousticness': features['acousticness'],
                    'instrumentalness': features['instrumentalness'],
                    'liveness': features['liveness'],
                    'valence': features['valence'],
                    'tempo': features['tempo']
                },
                'audio_analysis': {
                    'sections': len(analysis['sections']),
                    'segments_30s': {
                        'count': len(segments_30s),
                        'avg_loudness': sum(s['loudness_max'] for s in segments_30s) / len(segments_30s),
                        'avg_timbre': [
                            sum(s['timbre'][i] for s in segments_30s) / len(segments_30s)
                            for i in range(12)
                        ],
                        'avg_pitches': [
                            sum(s['pitches'][i] for s in segments_30s) / len(segments_30s)
                            for i in range(12)
                        ]
                    }
                }
            }
        except Exception as e:
            print(f"Error analyzing track: {str(e)}")
            return None

    def get_track_features(self, track_url):
        """Get track audio features and metadata"""
        try:
            track_id = self.extract_track_id(track_url)
            if not track_id:
                return None

            # Get track metadata
            track_info = self.sp.track(track_id)
            audio_features = self.sp.audio_features([track_id])[0]
            artist_id = track_info['artists'][0]['id']
            artist_info = self.sp.artist(artist_id)

            return {
                'track_name': track_info['name'],
                'artist_name': track_info['artists'][0]['name'],
                'album': track_info['album']['name'],
                'release_date': track_info['album']['release_date'],
                'popularity': track_info['popularity'],
                'artist_genres': artist_info['genres'],
                'artist_popularity': artist_info['popularity'],
                'audio_features': {
                    'danceability': audio_features['danceability'],
                    'energy': audio_features['energy'],
                    'key': audio_features['key'],
                    'loudness': audio_features['loudness'],
                    'tempo': audio_features['tempo'],
                    'valence': audio_features['valence'],
                    'instrumentalness': audio_features['instrumentalness']
                }
            }
        except Exception as e:
            print(f"Error analyzing track: {str(e)}")
            return None

    def get_artist_data(self, artist_id: str) -> Optional[Dict]:
        """Get artist data using the Spotify API"""
        try:
            artist = self.sp.artist(artist_id)
            if not artist or 'error' in artist:
                print(f"Error fetching artist data: {artist}")
                return None
            
            return {
                'profile': {
                    'id': artist['id'],
                    'name': artist['name'],
                    'genres': artist.get('genres', []),
                    'popularity': artist['popularity'],
                    'followers': artist['followers']['total'],
                    'image_url': artist['images'][0]['url'] if artist['images'] else None,
                    'spotify_url': artist['external_urls']['spotify']
                },
                'top_tracks': self.get_artist_top_tracks(artist_id),
                'related_artists': self.get_artist_related_artists(artist_id)
            }
        except Exception as e:
            print(f"Error fetching artist data: {e}")
            return None

    def get_artist_top_tracks(self, artist_id: str, market: str = 'US') -> List[Dict]:
        """Get top tracks for a given artist"""
        try:
            return self.sp.artist_top_tracks(artist_id, market=market)['tracks']
        except Exception as e:
            print(f"Error fetching top tracks for artist {artist_id}: {e}")
            return []

    def get_artist_related_artists(self, artist_id: str) -> List[Dict]:
        """Get related artists for a given artist"""
        try:
            return self.sp.artist_related_artists(artist_id)['artists']
        except Exception as e:
            print(f"Error fetching related artists for {artist_id}: {e}")
            return []

    def get_artist_albums(self, artist_id: str, include_groups: str = "album,single") -> List[Dict]:
        """Get albums for a given artist"""
        try:
            return self.sp.artist_albums(artist_id, include_groups=include_groups)['items']
        except Exception as e:
            print(f"Error fetching albums for artist {artist_id}: {e}")
            return []

    def extract_artist_id(self, url: str) -> Optional[str]:
        """Extract artist ID from Spotify URL or URI"""
        try:
            if 'artist/' in url:
                artist_id = url.split('artist/')[1].split('?')[0]
            elif 'spotify:artist:' in url:
                artist_id = url.split('spotify:artist:')[1]
            else:
                artist_id = url
            return artist_id
        except Exception as e:
            print(f"Error extracting artist ID: {e}")
            return None

    def get_artist_analysis(self, artist_id: str) -> Optional[Dict]:
        """Get comprehensive artist analysis including top tracks and related artists"""
        try:
            # Get artist profile
            artist = self.sp.artist(artist_id)
            
            # Get artist's top tracks
            top_tracks = self.sp.artist_top_tracks(artist_id)
            
            # Get related artists
            related = self.sp.artist_related_artists(artist_id)
            
            # Get artist's albums
            albums = self.sp.artist_albums(
                artist_id, 
                album_type='album,single', 
                limit=50
            )

            # Analyze top tracks audio features
            track_ids = [track['id'] for track in top_tracks['tracks']]
            audio_features = self.sp.audio_features(track_ids)

            analysis = {
                'profile': {
                    'name': artist['name'],
                    'genres': artist['genres'],
                    'popularity': artist['popularity'],
                    'followers': artist['followers']['total'],
                    'image_url': artist['images'][0]['url'] if artist['images'] else None
                },
                'top_tracks': [{
                    'name': track['name'],
                    'popularity': track['popularity'],
                    'album': track['album']['name'],
                    'release_date': track['album']['release_date'],
                    'preview_url': track['preview_url']
                } for track in top_tracks['tracks']],
                'audio_features_avg': self._calculate_avg_features(audio_features),
                'related_artists': [{
                    'name': artist['name'],
                    'genres': artist['genres'],
                    'popularity': artist['popularity']
                } for artist in related['artists'][:5]],
                'discography': {
                    'total_albums': len(albums['items']),
                    'latest_release': albums['items'][0] if albums['items'] else None,
                    'earliest_release': albums['items'][-1] if albums['items'] else None
                }
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing artist: {e}")
            return None

    def _calculate_avg_features(self, features: List[Dict]) -> Dict:
        """Calculate average audio features from a list of tracks"""
        if not features:
            return {}
            
        avg_features = {
            'danceability': 0,
            'energy': 0,
            'valence': 0,
            'tempo': 0,
            'instrumentalness': 0,
            'speechiness': 0
        }
        
        valid_features = [f for f in features if f is not None]
        if not valid_features:
            return avg_features
            
        for feature in valid_features:
            for key in avg_features.keys():
                avg_features[key] += feature[key]
                
        for key in avg_features.keys():
            avg_features[key] /= len(valid_features)
            
        return avg_features 

    def get_lastfm_data(self, artist_name: str) -> Optional[Dict]:
        """Get Last.fm artist data including similar artists and tags"""
        try:
            url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={artist_name}&api_key={LASTFM_API_KEY}&format=json"
            response = requests.get(url)
            data = response.json()
            
            return {
                'similar': [a['name'] for a in data.get('artist', {}).get('similar', {}).get('artist', [])[:5]],
                'tags': [t['name'] for t in data.get('artist', {}).get('tags', {}).get('tag', [])],
                'bio': data.get('artist', {}).get('bio', {}).get('summary', '')
            }
        except Exception as e:
            print(f"Last.fm API error: {e}")
            return None

    def generate_ar_report(self, artist_data) -> Optional[str]:
        """Generate A&R report prompt from artist data"""
        try:
            lastfm_data = self.get_lastfm_data(artist_data['profile']['name'])
            prompt = f"""As an AI-powered A&R specialist, analyze this artist's potential:
            
Artist: {artist_data['profile']['name']}
Genres: {', '.join(artist_data['profile']['genres'])}
Popularity: {artist_data['profile']['popularity']}/100
Followers: {artist_data['profile']['followers']}

-- Last.fm Data --
Similar Artists: {', '.join(lastfm_data['similar']) if lastfm_data and lastfm_data.get('similar') else 'N/A'}
Top Tags: {', '.join(lastfm_data['tags']) if lastfm_data and lastfm_data.get('tags') else 'N/A'}
Bio Summary: {lastfm_data['bio'][:300] + '...' if lastfm_data and lastfm_data.get('bio') else 'N/A'}

Spotify Analysis:
Top Tracks: {', '.join(track['name'] for track in artist_data['top_tracks']) if artist_data.get('top_tracks') else 'No top tracks available'}
Similar Artists: {', '.join(artist['name'] for artist in artist_data['related_artists']) if artist_data.get('related_artists') else 'No similar artists available'}

Please provide a detailed A&R report covering:
1. Market Position & Potential
2. Genre Analysis
3. Artist Development
4. Strategic Recommendations

Format the analysis in clear sections with bullet points where appropriate."""
            return prompt
        except Exception as e:
            print(f"Error generating A&R report prompt: {e}")
            return None

    def analyze_user_taste(self, time_range='long_term', limit=5):
        """Analyze user's music taste based on top tracks"""
        try:
            # Get user's top tracks
            top_tracks = self.sp.current_user_top_tracks(
                limit=limit,
                offset=0,
                time_range=time_range
            )

            # Get audio features for all tracks
            track_ids = [track['id'] for track in top_tracks['items']]
            audio_features = self.sp.audio_features(track_ids)

            # Collect track and artist data
            tracks_data = []
            for track, features in zip(top_tracks['items'], audio_features):
                artist_id = track['artists'][0]['id']
                artist_info = self.sp.artist(artist_id)
                
                tracks_data.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'genres': artist_info['genres'],
                    'popularity': track['popularity'],
                    'features': {
                        'danceability': features['danceability'],
                        'energy': features['energy'],
                        'valence': features['valence'],
                        'tempo': features['tempo'],
                        'key': features['key']
                    }
                })

            return {
                'tracks_data': tracks_data,
                'analysis_prompt': self._format_tracks_for_prompt(tracks_data)
            }
            
        except Exception as e:
            print(f"Error analyzing user taste: {e}")
            return None

    def _format_tracks_for_prompt(self, tracks_data):
        """Format tracks data for the AI prompt"""
        formatted = []
        for track in tracks_data:
            formatted.append(
                f"Track: {track['name']} by {track['artist']}\n"
                f"Genres: {', '.join(track['genres'])}\n"
                f"Popularity: {track['popularity']}\n"
                f"Features: Energy={track['features']['energy']:.2f}, "
                f"Danceability={track['features']['danceability']:.2f}, "
                f"Valence={track['features']['valence']:.2f}\n"
            )
        return "\n".join(formatted) 