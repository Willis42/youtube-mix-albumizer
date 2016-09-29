#!/usr/bin/env python3

import argparse
import json
import re

#dependencies
import youtube_dl
import pydub

youtube_dlr = youtube_dl.YoutubeDL()

def download_video(url):
    return youtube_dlr.extract_info(url)

def tracks_from_description(desc):
    tracklist = desc[desc.find('Tracklist'):]
    tracks = [tuple(re.split('(?<=\d\d:\d\d)\s+', t)) for t in tracklist.split('\n') if re.fullmatch('\d\d:\d\d.+', t)]
    return tracks

def get_start_time_in_millis(track):
    clocktime = track[0].split(':')
    minutes, seconds = int(clocktime[0]), int(clocktime[1])
    return (minutes * 60 + seconds) * 1000



def split_from_filenames(video_filename, info_filename, outdir=''):
    info = None
    with open(info_filename) as info_file:
        info = json.load(info_file)

    tracks = tracks_from_description(info['description'])
    print(tracks)
    
    audio = pydub.AudioSegment.from_file(video_filename)
    for i in range(len(tracks)):
        start = get_start_time_in_millis(tracks[i])
        end = len(audio)
        if i < len(tracks) - 1:
            end = get_start_time_in_millis(tracks[i+1])

        piece = audio[start:end]
        artist, title = tuple(re.split('\s*-\s*', tracks[i][1]))
        tags = {'artist': artist, 'title': title, 'album': info['title'], 'track': i+1}
        filename = outdir + tracks[i][1] + '.mp3'
        
        print('exporting ' + filename + '...')
        piece.export(filename, tags=tags)
    
    print('done!')

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--vidfile', help='path of the input video file to be split into an album')
    arg_parser.add_argument('--infofile', help='path of the info file')
    arg_parser.add_argument('--outdir', help='path of the directory to output the album into')
    
    args=arg_parser.parse_args()
    video_filename = args.vidfile
    if video_filename is None:
        video_filename = input('what\'s the path for the video file? ')
    info_filename = args.infofile
    if info_filename is None:
        info_filename = input('what\'s the path for the info file? ')
    outdir = args.outdir or ''
    
    print('OK! attempting to split...')
    split_from_filenames(video_filename, info_filename, outdir)