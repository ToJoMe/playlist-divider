# import packages
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class PlaylistDivider:
    """ The PlaylistDivider object partitions a current playlist on users spotify into genre based subplaylists.

        Args:
            username (str): username of the user to identify themself and the playlist
            client_id (str): client_id for the application can be found and set in developer account
            client_secret (str): client_secret for the application can be found and set in developer account
            playlist_id (str): id of the playlist to retrieve the tracks to divide
            num_playlists (int): number of subplaylist to generate

        """
    def __init__(self, username, client_id, client_secret, playlist_id, num_playlists=None):
        self.username = username
        self.client_id = client_id
        self.client_secret = client_secret
        self.playlist_id = playlist_id
        self.num_playlists = num_playlists
        
    def create_spotify_object(self, client_id, client_secret, scopes):
        """ Function creates a spotify object to work with the Spotify-API-Endpoints

        Args:
            client_id (str): client_id for the application can be found and set in developer account
            client_secret (str): client_secret for the application can be found and set in developer account
            scopes (list): scopes that are allowed to be accessed by the object

        """
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=client_secret,
                                                redirect_uri='http://localhost:7777/callback',
                                                scope=scopes))
        
        return sp
    
    def get_playlist_tracks(self, sp ,username, playlist_id):
        """ Function that access a current playlist of the user and returns a dataframe with the tracks

        Args:
            sp (object): created spotify object to communicat with the spofitfy endpoints
            username (str): username of the user to identify themself and the playlist
            playlist_id (str): id of the playlist to retrieve the tracks to divide

        Returns:
            dataframe: dataframe with tracks, artists and their ids
        """
        # get tracks in playlist
        results = sp.user_playlist_tracks(username,playlist_id)
        response = results['items']
        while results['next']:
            results = sp.next(results)
            response.extend(results['items'])
                        
        # get number of tracks
        number_tracks = len(response)  
        # list for storage
        artists_ids = []
        track_ids = []
        # build dataframe
        for i in range(number_tracks):
            # artist infos
            artists_ids.append(response[i]['track']['album']['artists'][0]['id'])
            # track infos
            track_ids.append(response[i]['track']['id'])


        df_playlist_tracks = pd.DataFrame(zip(artists_ids, track_ids), columns=['artist_id', 'track_id'])

        return df_playlist_tracks    

    def get_artist_genres(self, sp, df_tracks):
        """ Function that creates a dataframe with artists in the playlist and their genre

        Args:
            sp (object): created spotify object to communicat with the spofitfy endpoints
            df_tracks (dataframe): dataframe to divide 

        Returns:
            dataframe: artists with their genre
        """
        # find unique artists in dataframe
        artist_ids_list = df_tracks['artist_id'].unique().tolist()
        
        # get genre for each artist
        artist_ids = []
        artist_genres = []

        for id in artist_ids_list:
            response_artist = sp.artist(f"spotify:artist:{id}")
            artist_ids.append(response_artist['id'])
            artist_genres.append(response_artist['genres'])
        
        df_artist_genres = pd.DataFrame(zip(artist_ids, artist_genres), columns=['artist_id', 'artist_genres'])
        
        # Drop rows with empty lists
        df_artist_genres = df_artist_genres[df_artist_genres['artist_genres'].apply(lambda x: len(x) > 0)].reset_index(drop=True)
        # reduce to only one genre - probably the shortes ones - main music genre no subgroups
        df_artist_genres['genre'] = df_artist_genres['artist_genres'].apply(lambda x: min(x, key=len))

        return df_artist_genres

    def merge_dataframes(self, df_tracks, df_genres):
        """ Function to merge the dataframes together

        Args:
            df_tracks (dataframe): includes tracks, artists and their ids
            df_genres (dataframe): includes artists and their genres

        Returns:
            dataframe: merged dataframe of tracks and genres
        """
        df_merged = pd.merge(df_tracks, df_genres[['artist_id', 'genre']], on=['artist_id'])    
        return df_merged

    def get_top_genres(self, df, n):
        """ Function to extract the top n genres of the dataframe based on counts

        Args:
            df (dataframe): dataframe with tracks, artists and their genres
            n (int): number of top genres to extract

        Returns:
            list: list of top genres
        """
        # get the value counts of the 'genre' column
        counts = df['genre'].value_counts()
        # create a new dataframe from the value counts
        df_counts = pd.DataFrame({'genre': counts.index, 'count': counts.values})
        # get the top n genres as a list
        top_genres = df_counts.nlargest(n, 'count')['genre'].tolist()
        
        return top_genres

    def get_all_genres(self, df):
        """ Function to extract the all genres of the dataframe based on counts

        Args:
            df (dataframe): dataframe with tracks, artists and their genres
            n (int): number of top genres to extract

        Returns:
            list: list of top genres
        """
        # get the value counts of the 'genre' column
        counts = df['genre'].value_counts()
        # create a new dataframe from the value counts
        df_counts = pd.DataFrame({'genre': counts.index, 'count': counts.values})
        # get the top n genres as a list
        all_genres = df_counts['genre'].tolist()
        
        return all_genres

    def create_top_genre_dataframe(self, df, top_genres):
        """ Function to create top genre dataframe

        Args:
            df (dataframe): dataframe that is based on
            top_genres (list): list of top genres to extract

        Returns:
            dataframe: dataframe with only relevant top genre tracks
        """
        df_relevant = df.loc[df['genre'].isin(top_genres)].reset_index(drop=True)
        return df_relevant
    
    def divide_dataframe_by_column(self, df, column_name):
        """ Function that divides a dataframe into smaller dataframes based on unique values in a specified column

        Args:
            df (dataframe): frame that should be split into smaller dataframes
            column_name (str): the name of the column to divide the DataFrame by

        Returns:
            dictionary : dict of dataframes, where each dataframe contains only the rows with a unique value in the specified column
        """
        unique_values = df[column_name].unique()
        grouped_data = {}
        for value in unique_values:
            grouped_data[value] = df[df[column_name] == value]
        return grouped_data

    def create_new_playlist(self, sp, username, playlist_name):
        """ Function that creates a new playlist inside users player

        Args:
            sp (object): created spotify object to communicat with the spofitfy endpoints
            username (str): username to identify the user
            playlist_name (str): name of the playlist
        """
        sp.user_playlist_create(username, name=playlist_name)
        print("Playlist successfully created!")

    def get_current_playlists(self, sp, username):
        """ Function that retrievs users current playlists

        Args:
            sp (object): created spotify object to communicat with the spofitfy endpoints
            username (str): username to identify the user

        Returns:
            dataframe : includes playlistnames and playlist_ids
        """
        results = sp.current_user_playlists(limit=50)
        response = results['items']
        while results['next']:
            results = sp.next(results)
            response.extend(results['items'])
            
        # get number of playlists
        number_playlists = len(response)  
        playlist_names = []
        playlist_ids = []
        for i in range(number_playlists):
            playlist_names.append(response[i]['name'])
            playlist_ids.append(response[i]['id'])
            
        # create dataframe 
        df_playlists = pd.DataFrame(zip(playlist_names, playlist_ids), columns=['playlist_name', 'playlist_id'])
        
        return df_playlists

    def find_playlist_ids(self, df, playlist_names):
        """ Function that find playlist ids

        Args:
            df (dataframe): dataframe of all current playlist of the user
            playlist_names (list): list of created playlists

        Returns:
            dictionary : includes playlist names and the ids
        """
        # search for a certain playlist name and store the playlist_id in a dictionary
        dict_playlist_ids = {}
        
        for name in playlist_names:
            for i, row in df.iterrows():
                if name in row['playlist_name']:
                    dict_playlist_ids[row['playlist_name']] = row['playlist_id']
                    
        return dict_playlist_ids

    def add_tracks_to_playlist(self, sp, username, dict_playlists, top_genres, grouped_data):
        """ Functions that adds tracks to playlist

        Args:
            sp (object): created spotify object to communicat with the spofitfy endpoints
            username (str): username to identify the user
            dict_playlists (dict): dictionary with playlist names and the ids
            top_genres (list): names of top genres
            grouped_data (dict): dictionary with dataframes for the certain genres
        """
        # iterate through each genre and dataframe and add songs to the created playlists
        for genre in top_genres:
            playlist_id = dict_playlists[genre]
            df_tracks = grouped_data[genre]
            track_ids = df_tracks['track_id'].unique().tolist()
            # make subset of dataframe of max 100 for API-Calls
            n = 100
            sub_track_list = [track_ids[i:i + n] for i in range(0, len(track_ids), n)]
            # add tracks to playlist
            for i in range(len(sub_track_list)):
                sp.user_playlist_add_tracks(username, playlist_id, sub_track_list[i])
        
        print("Tracks successfully added to playlists!")

    def run_partition(self, div_type=None):
        scopes = ["user-follow-read", 'ugc-image-upload', 'user-read-playback-state',
          'user-modify-playback-state', 'user-read-currently-playing', 'user-read-private',
          'user-read-email', 'user-follow-modify', 'user-follow-read', 'user-library-modify',
          'user-library-read', 'streaming', 'app-remote-control', 'user-read-playback-position',
          'user-top-read', 'user-read-recently-played', 'playlist-modify-private', 'playlist-read-collaborative',
          'playlist-read-private', 'playlist-modify-public']
        
        sp = self.create_spotify_object(self.client_id, self.client_secret, scopes)
        df_playlist_tracks = self.get_playlist_tracks(sp, self.username, self.playlist_id)
        df_artist_genres = self.get_artist_genres(sp, df_playlist_tracks)
        df_final = self.merge_dataframes(df_playlist_tracks, df_artist_genres)
        
        if div_type == 'complete':
            all_genres = self.get_all_genres(df_final)
            grouped_data = self.divide_dataframe_by_column(df_final, 'genre')
            
            # create playlist for each genre
            for genre in all_genres:
                self.create_new_playlist(sp, self.username, genre)
                
            df_playlists = self.get_current_playlists(sp, self.username)
            dict_playlists = self.find_playlist_ids(df_playlists, all_genres)
            self.add_tracks_to_playlist(sp, self.username, dict_playlists, all_genres, grouped_data)
            
        else:
            top_genres = self.get_top_genres(df_final, self.num_playlists)
            df_top = self.create_top_genre_dataframe(df_final, top_genres)
            grouped_data = self.divide_dataframe_by_column(df_top, 'genre')
            
            # create playlist for each top genre
            for genre in top_genres:
                self.create_new_playlist(sp, self.username, genre)
            
            df_playlists = self.get_current_playlists(sp, self.username)
            dict_playlists = self.find_playlist_ids(df_playlists, top_genres)
            self.add_tracks_to_playlist(sp, self.username, dict_playlists, top_genres, grouped_data)
        
   
if __name__ == '__main__':
    username = input("Enter your username: ")
    client_id = input("Enter your client-id: ")
    client_secret = input("Enter your client-secret: ")
    playlist_id = input("Enter your playlist-id: ")
    division_type = input("Do you want the full playlist divided? (yes/no) ")
    if division_type == 'yes':
        playlist_divider = PlaylistDivider(username, client_id, client_secret, playlist_id)
        playlist_divider.run_partition('complete')
    else:
        num_playlist = int(input("Enter the number of playlists to create: "))
        playlist_divider = PlaylistDivider(username, client_id, client_secret, playlist_id, num_playlist)
        playlist_divider.run_partition()
        