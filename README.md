# Music Analysis Hub 🎵

A Streamlit application that provides comprehensive music analysis tools using Spotify and Last.fm data, powered by AI insights through DeepSeek API.

## Features

### 1. Artist Analysis
- Detailed artist profile and metrics
- Top tracks and albums
- Related artists with popularity scores
- Genre analysis and categorization
- Visual representation of artist data

### 2. A&R Reports
- AI-generated A&R analysis reports
- Last.fm integration for community insights
- Downloadable reports including:
  - Market position & potential
  - Genre analysis
  - Artist development recommendations
  - Strategic insights

### 3. Music Taste Analysis
- Personal music taste analysis based on:
  - Last 4 weeks
  - Last 6 months
  - All time listening history
- Track-by-track breakdown with audio features
- AI-powered insights about listening patterns

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/music-analysis-hub.git
cd music-analysis-hub
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
DEEPSEEK_API_KEY=your_deepseek_api_key
LASTFM_API_KEY=your_lastfm_api_key
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Enter a Spotify artist URL or ID in the search bar
3. Navigate between tabs to access different features:
   - Artist Data
   - A&R Report
   - Taste Analysis

## Code Structure

- `app.py`: Main Streamlit application interface
- `spotify_helper.py`: Spotify and Last.fm API integrations
- `test_deepseek.py`: DeepSeek API integration for AI analysis

## Dependencies


```1:5:requirements.txt
openai>=1.0.0
python-dotenv>=0.19.0 
streamlit>=1.30.0
spotipy>=2.23.0
requests>=2.31.0 
```


## API References

The application uses three main APIs:
1. Spotify API (via `spotipy`)
2. Last.fm API (for community data)
3. DeepSeek API (for AI analysis)

## Features in Detail

### Artist Analysis

```82:140:app.py
def display_artist_data(artist_data):
    """Display artist data in a structured format"""
    if not artist_data:
        st.error("Unable to fetch artist data. Please check the artist ID or URL.")
        return

    # Artist Profile
    st.header(artist_data['profile']['name'])
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if artist_data['profile']['image_url']:
            st.image(artist_data['profile']['image_url'])
    
    with col2:
        st.subheader("Artist Profile")
        st.write(f"**Genres:** {', '.join(artist_data['profile']['genres']) if artist_data['profile']['genres'] else 'No genres available'}")
        st.metric("Popularity Score", artist_data['profile']['popularity'])
        st.metric("Followers", f"{artist_data['profile']['followers']:,}")
        st.write(f"[Open in Spotify]({artist_data['profile']['spotify_url']})")

    # Top Tracks
    if artist_data.get('top_tracks'):
        st.subheader("Top Tracks")
        for track in artist_data['top_tracks']:
            with st.expander(track['name']):
                st.write(f"Popularity: {track['popularity']}")
                if track['preview_url']:
                    st.audio(track['preview_url'])
                st.write(f"[Open in Spotify]({track['external_urls']['spotify']})")
    else:
        st.write("No top tracks available for this artist.")
    # Related Artists
    if artist_data.get('related_artists'):
        st.subheader("Similar Artists")
        cols = st.columns(3)
        for idx, artist in enumerate(artist_data['related_artists']):
            with cols[idx % 3]:
                st.write(f"**{artist['name']}**")
                st.write(f"Genres: {', '.join(artist['genres']) if artist['genres'] else 'No genres available'}")
                st.metric("Popularity", artist['popularity'])
                if artist['images']:
                    st.image(artist['images'][0]['url'], width=100)
                st.write(f"[Open in Spotify]({artist['external_urls']['spotify']})")
    else:
        st.write("No similar artists available.")

    # Fetch and display albums
    spotify = SpotifyAnalyzer()
    albums = spotify.get_artist_albums(artist_data['profile']['id'])
    if albums:
        st.subheader("Albums")
        for album in albums:
            st.write(f"**{album['name']}**")
            st.write(f"Release Date: {album['release_date']}")
            st.write(f"[Open in Spotify]({album['external_urls']['spotify']})")
    else:
        st.write("No albums available for this artist.")
```


### A&R Report Generation

```434:464:spotify_helper.py
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
```


### Music Taste Analysis

```142:187:app.py
def display_taste_analysis():
    """Display user's music taste analysis"""
    st.subheader("Your Music Taste Analysis")
    
    time_range = st.select_slider(
        "Analysis Period",
        options=[
            ("short_term", "Last 4 Weeks"),
            ("medium_term", "Last 6 Months"),
            ("long_term", "All Time")
        ],
        format_func=lambda x: x[1]
    )

    if st.button("Analyze My Music Taste"):
        with st.spinner("Analyzing your music preferences..."):
            spotify = SpotifyAnalyzer()
            analysis = spotify.analyze_user_taste(time_range=time_range[0])
            
            if analysis:
                # Display track data
                st.write("### Your Top Tracks")
                for track in analysis['tracks_data']:
                    with st.expander(f"{track['name']} by {track['artist']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Genres:**", ", ".join(track['genres']))
                            st.metric("Popularity", track['popularity'])
                        with col2:
                            for name, value in track['features'].items():
                                st.metric(name.title(), f"{value:.2f}")

                # Generate AI insights using imported client
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are an expert music analyst specializing in user behavior and music trends."},
                        {"role": "user", "content": analysis['analysis_prompt']}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                st.write("### AI Insights")
                st.markdown(response.choices[0].message.content)
```


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Spotify Web API
- Last.fm API
- DeepSeek API
- Streamlit Community
