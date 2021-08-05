from http.client import HTTPResponse
from math import ceil
import re
from subprocess import Popen, PIPE, DEVNULL
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
from urllib.request import urlopen

from pytube import YouTube
from pytube.query import StreamQuery
from tqdm import tqdm


def is_valid_youtube_url(url: str) -> bool:
    if not url:
        return False

    if not url.startswith('http'):
        url = f'https://{url}'

    try:
        resp: HTTPResponse = urlopen(url)
        if resp.getcode() == 200 and 'youtube.com' in urlparse(resp.geturl()).netloc:
            return True
    except Exception:
        return False

    return False


def get_clean_string(string: str) -> str:
    string: str = ''.join(char for char in string if char not in set(r'/\?%*:|"<>.'))
    string: str = re.sub(' {2,}', ' ', string)

    return string


def get_audio_info(url: str) -> Optional[Dict[str, str]]:
    content: YouTube = YouTube(url)
    audio_streams: StreamQuery = content.streams.filter(only_audio=True).order_by("abr").desc()

    if audio_streams:
        channel: str = get_clean_string(content.author)
        title: str = get_clean_string(content.title)

        if channel not in title:
            title = f'{channel} - {title}'

        info: Dict[str, str] = {
            'title': f'{title}',
            'btr': audio_streams[0].abr.strip('bps'),
            'url': audio_streams[0].url
        }

        return info

    return


def get_mp3(info: Dict[str, str]) -> None:
    print(f'File name: {info["title"]}, bitrate: {info["btr"]}bps')
    print('Downloading...')

    response: HTTPResponse = urlopen(info['url'])
    command: Tuple = ('ffmpeg', '-y', '-i', '-', '-b:a', f"{info['btr']}", f"mp3/{info['title']}.mp3")
    process: Popen = Popen(command, stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)

    size: str = response.headers['content-length']
    chunk_size: int = 16*1024
    num_chunks: int = ceil(int(size) / chunk_size)

    for _ in tqdm(range(num_chunks)):
        chunk: bytes = response.read(chunk_size)
        if not chunk:
            break
        process.stdin.write(chunk)

    process.stdin.close()
    process.wait()


def main() -> None:
    url: str = ''

    while not is_valid_youtube_url(url):
        url = input('Enter video url: ')

    info = get_audio_info(url)

    if info:
        get_mp3(info)
    else:
        print('No audio streams')

    print('Done!')


if __name__ == '__main__':
    main()
