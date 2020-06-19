from math import ceil
from subprocess import Popen, PIPE, DEVNULL
from urllib.request import urlopen

import pytube
from tqdm import tqdm


def clean_string(string):
    for char in r'/\?%*:|"<>.':
        string = string.replace(char, '')
    if '  ' in string:
        string = string.replace('  ', ' ')
    return string


def get_audio_info(url):
    content = pytube.YouTube(url)
    audio_streams = content.streams.filter(only_audio=True).order_by("abr").desc()

    if audio_streams:
        channel = clean_string(content.author)
        title = clean_string(content.title)

        if channel not in title:
            title = f'{channel} - {title}'

        info = {
            'title': f'{title}',
            'btr': audio_streams[0].abr.strip('bps'),
            'url': audio_streams[0].url
        }

        return info
    return


def get_mp3(info):
    print(f'Downloading mp3: {info["title"]}')
    response = urlopen(info['url'])
    command = ('ffmpeg', '-y', '-i', '-', '-b:a', f"{info['btr']}", f"{info['title']}.mp3")
    process = Popen(command, stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)

    size = response.headers['content-length']
    chunk_size = 16*1024
    num_chunks = ceil(int(size) / chunk_size)

    for _ in tqdm(range(num_chunks)):
        chunk = response.read(chunk_size)
        if not chunk:
            break
        process.stdin.write(chunk)

    process.stdin.close()
    process.wait()


def main():
    url = input('Enter video url: ')
    info = get_audio_info(url)
    if info:
        get_mp3(info)
    else:
        print('No audio streams')
    print('Done!')


if __name__ == '__main__':
    main()
