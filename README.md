# Spotify Playlist Genre Splitter

This Python program lets a Spotify user divide a playlist based on the genre of the artist into sub playlists. The program takes in a playlist ID, and based on the genre of the artists in the playlist, creates genre-based sub playlists. This helps the user to categorize the songs in the playlist based on the genres and makes it easy for them to find their favorite songs.

## Problem Statement

Sometimes users create playlists and save their favorite songs there without any categorization based on genres. If the user now wants to divide the playlist again, they have to do it manually. This program allows users to divide a certain playlist automatically and create genre-based sub playlists, and now the user gets all songs ordered into certain genre playlists.

## Prerequisites

* Spotify developer account (more information here: https://developer.spotify.com/documentation/web-api/tutorials/getting-started)
* Spotify client ID and secret key
* Python 3.x

## Usage

1. Create a Spotify developer account and create a new application to get your client ID and secret key.
2. Install the necessary libraries using pip install -r requirements.txt.
3. Run the script main.py and enter your Spotify username, playlist ID, client ID, and client secret.
4. Choose whether you want to split the playlist into top genres or split the full playlist into all possible sub-genres.
5. The program will create a new playlist for each genre and add the songs from the original playlist to the corresponding genre playlists.

## How it works

The program uses the Spotipy library to access the Spotify API and retrieve the playlist's track information. It then uses the Spotify Web API to get the track information, including the artists' names. The program then extracts the genres of the artists from the Spotify API and creates new playlists based on the genres. Finally, it adds the songs from the original playlist to the corresponding genre playlists.