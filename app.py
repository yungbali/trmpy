import streamlit as st
from test_deepseek import analyze_music, scout_talent, client
from spotify_helper import SpotifyAnalyzer
from datetime import datetime
import os

def display_ar_report(artist_data):
    """Display AI-generated A&R report"""
    try:
        # Ensure the SpotifyAnalyzer instance is created
        spotify = SpotifyAnalyzer()
        
        # Generate the A&R report prompt
        prompt = spotify.generate_ar_report(artist_data)
        
        if prompt:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an experienced A&R specialist with deep knowledge of the music industry, artist development, and market trends."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            report = response.choices[0].message.content
            
            # Display the report in a structured way
            st.subheader("🎯 A&R Analysis Report")
            st.markdown(report)
            
            # Add download button for the report
            st.download_button(
                label="Download A&R Report",
                data=f"""A&R Report for {artist_data['profile']['name']}\n
                Generated on {datetime.now().strftime('%Y-%m-%d')}\n\n
                {report}""",
                file_name=f"ar_report_{artist_data['profile']['name'].lower().replace(' ', '_')}.txt",
                mime="text/plain"
            )
        else:
            st.error("Failed to generate A&R report prompt.")
            
    except Exception as e:
        st.error(f"Error generating A&R report: {str(e)}")

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

def main():
    # Main app content
    st.title("🎵 Music Analysis Hub")
    
    # Create tabs
    data_tab, report_tab, taste_tab = st.tabs(["Artist Data", "A&R Report", "Taste Analysis"])
    
    with data_tab:
        st.header("Artist Analysis")
        artist_input = st.text_input(
            "Enter Spotify Artist URL or ID",
            placeholder="https://open.spotify.com/artist/... or artist ID"
        )
        
        if st.button("Analyze Artist"):
            if artist_input:
                with st.spinner("Analyzing artist..."):
                    spotify = SpotifyAnalyzer()
                    artist_id = spotify.extract_artist_id(artist_input)
                    if artist_id:
                        artist_data = spotify.get_artist_data(artist_id)
                        display_artist_data(artist_data)
                        
                        # Only generate the A&R report if artist_data is valid
                        if artist_data:
                            with report_tab:
                                display_ar_report(artist_data)
                    else:
                        st.error("Invalid artist URL or ID")
            else:
                st.warning("Please enter an artist URL or ID")
    
    with taste_tab:
        display_taste_analysis()

if __name__ == "__main__":
    main() 