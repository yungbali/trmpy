from openai import OpenAI
import os
from dotenv import load_dotenv
from spotify_helper import SpotifyAnalyzer

# Load environment variables
load_dotenv()

# Initialize the clients
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)
spotify = SpotifyAnalyzer()

def analyze_music(artist_name=None, song_url=None, genre=None):
    try:
        # Get Spotify track analysis
        track_data = spotify.get_track_features(song_url) if song_url else None
        
        system_prompt = """You are an AI-powered Music Strategist and A&R specialist focused on African music. 
        Analyze the provided information including Spotify metrics and audio features to give insights about:
        1. Musical elements and production quality
        2. Market potential and target audience
        3. Cultural relevance and authenticity
        4. Recommendations for growth and development
        """
        
        user_prompt = f"""Please analyze the following artist/song:
        Artist: {artist_name}
        Genre: {genre}
        Song URL: {song_url}
        
        Spotify Analysis:
        {track_data if track_data else 'No Spotify data available'}
        """
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error occurred: {str(e)}"

def scout_talent(region=None, genre=None):
    try:
        system_prompt = """You are an AI-powered A&R specialist focused on discovering emerging African talent.
        Using @Web, search for and analyze:
        1. Emerging artists in the specified region/genre
        2. Streaming and social media metrics
        3. Recent breakthrough moments
        4. Market potential and unique selling points
        5. Recommendations for artist development
        """
        
        user_prompt = f"Scout for emerging talent in:\nRegion: {region}\nGenre: {genre}\nProvide a detailed report on the top 3 promising artists."
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        print("\n=== Talent Scouting Report ===")
        print(response.choices[0].message.content)
        print("\nUsage Stats:")
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Completion tokens: {response.usage.completion_tokens}")
        print(f"Total tokens: {response.usage.total_tokens}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    # Example usage
    analyze_music(
        artist_name="Rema",
        song_url="https://example.com/calm-down",
        genre="Afrobeats"
    )
    
    scout_talent(
        region="West Africa",
        genre="Amapiano"
    ) 