from pytube import Playlist

def parse_playlist(playlist_url):
    # Returns all the links of videos present in a given YouTube playlist
    playlist = Playlist(playlist_url)
    for video in playlist.videos[:3]:
        title = video.title
        _, name, index = title.split('-')
        name = name.strip()
        index = index.strip()[1:-1]
        print(f"ID: {video.video_id}, index: {index}, title: {name}")


if __name__ == '__main__':
    # let user enter the playlist url and then call function to extract video urls
    playlist_url = input("Enter your youtube playlist: ")
    parse_playlist(playlist_url)
