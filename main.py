import argparse
import mimetypes
import os

from mutagen import File
from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3


def create_parser():
    parser = argparse.ArgumentParser(description="Edit tags for an audio file.")
    parser.add_argument("file_path", help="Path to the audio file")
    parser.add_argument("--title", help="Title of the track")
    parser.add_argument("--artist", help="Artist of the track")
    parser.add_argument("--album", help="Album of the track")
    parser.add_argument("--year", help="Year of the track")
    parser.add_argument("--list", action="store_true", help="List current tags of the audio file")
    parser.add_argument("--cover", help="Path to the image file to be used as album cover")

    return parser


def _get_audio(file_path: str):
    audio = File(file_path, easy=True)

    if audio is None:
        raise ValueError(f"Unsupported file format: {file_path}")

    return audio


def list_tags(file_path: str):
    try:
        audio = _get_audio(file_path)
        print(f"Tags for {file_path}:")
        for tag, value in audio.tags.items():
            print(f"{tag}: {value}")

    except Exception as e:
        print(f"An error occurred: {e}")


def edit_tags(
        file_path: str,
        title: str = None,
        artist: str = None,
        album: str = None,
        year: str = None,
        cover: str = None
):
    try:
        audio = _get_audio(file_path)

        if title:
            audio['title'] = [title]
        if artist:
            audio['artist'] = [artist]
        if album:
            audio['album'] = [album]
        if year:
            audio['date'] = [year]
        if cover:
            add_album_cover(file_path, cover)

        audio.save()
        print(f"Tags updated successfully for {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def add_album_cover(file_path, cover_path):
    mime, _ = mimetypes.guess_type(cover_path)
    if not mime:
        raise ValueError("Cannot determine MIME type of the cover image.")

    with open(cover_path, "rb") as cover_file:
        cover_data = cover_file.read()

    if file_path.lower().endswith('.mp3'):
        audio = MP3(file_path, ID3=ID3)
        audio.tags.add(
            APIC(
                encoding=3,  # 3 is for UTF-8
                mime=mime,  # image/jpeg or image/png
                type=3,  # 3 is for the cover(front) image
                desc=u'Cover',
                data=cover_data
            )
        )
    elif file_path.lower().endswith('.flac'):
        audio = FLAC(file_path)
        image = Picture()
        image.type = 3
        image.mime = mime
        image.desc = u'Cover'
        image.data = cover_data
        audio.clear_pictures()
        audio.add_picture(image)
    else:
        print(f"Cover image addition not supported for this file format: {file_path}")


def main():
    parser = create_parser()
    args = parser.parse_args()

    path = os.path.expanduser(args.file_path)
    if cover := args.cover:
        cover = os.path.expanduser(cover)

    if args.list:
        list_tags(path)
    else:
        edit_tags(path, args.title, args.artist, args.album, args.year, cover)


if __name__ == "__main__":
    main()
