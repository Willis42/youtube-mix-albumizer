#!/usr/bin/env python3

import argparse
import json
import re
import os
from urllib import request

#dependencies
import youtube_dl
import pydub

youtube_dlr = youtube_dl.YoutubeDL()

def download_video(url):
    return youtube_dlr.extract_info(url)

def tracks_from_description(desc):
    tracklist = desc[desc.find('Tracklist'):]
    tracks = [tuple(re.split('(?<=\d:\d\d)\s+', t)) for t in tracklist.split('\n') if re.fullmatch('\d+:\d\d.+', t)]
    return tracks

def get_start_time_in_millis(track):
    clocktime = track[0].split(':')
    minutes, seconds = int(clocktime[0]), int(clocktime[1])
    return (minutes * 60 + seconds) * 1000



def split_from_filenames(video_filename, info_filename=None, outdir=None, info = None):
    assert((info_filename or info) is not None)
    
    if info is None:
        with open(info_filename) as info_file:
            info = json.load(info_file)
    
    if outdir is None:
        outdir = info['title'] + '/'

    tracks = tracks_from_description(info['description'])
    print(tracks)
    
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
        
    with request.urlopen(info['thumbnail']) as thumbnail_file:
        with open(outdir + 'thumbnail_img.jpg', 'wb') as out:
            out.write(thumbnail_file.read())
    
    audio = pydub.AudioSegment.from_file(video_filename)
    for i in range(len(tracks)):
        start = get_start_time_in_millis(tracks[i])
        end = len(audio)
        if i < len(tracks) - 1:
            end = get_start_time_in_millis(tracks[i+1])

        piece = audio[start:end]
        title = tracks[i][1]
        artist = ''
        as_tuple = tuple(re.split('\s*-\s*', title))
        if len(as_tuple) == 2:
            artist = as_tuple[0]
            title = as_tuple[1]
        if len(as_tuple) > 2:
            print('WARNING: split title has more than 2 parts:', as_tuple)
        tags = {'artist': artist, 'title': title, 'album': info['title'], 'track': i+1}
        filename = outdir + tracks[i][1] + '.mp3'
        
        print('exporting ' + filename + '...')
        piece.export(filename, tags=tags)
    
    print('done!')

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--url', help='url of the YouTube video to be downloaded')
    arg_parser.add_argument('--vidfile', help='path of the input video file to be split into an album')
    arg_parser.add_argument('--infofile', help='path of the info file')
    arg_parser.add_argument('--outdir', help='path of the directory to output the album into')
    
    args=arg_parser.parse_args()
    if args.url:
        info = download_video(args.url)
        video_filename = info['title'] + '-' + info['display_id'] + '.mkv'
        info_filename = info['title'] + '-' + info['display_id'] + '.json'
        with open(info_filename, 'w') as out:
            json.dump(info, out)
    else:
        video_filename = args.vidfile
        if video_filename is None:
            video_filename = input('what\'s the path for the video file? ')
        info_filename = args.infofile
        if info_filename is None:
            info_filename = input('what\'s the path for the info file? ')
            
    outdir = args.outdir
    
    print('OK! attempting to split...')
    split_from_filenames(video_filename, info_filename, outdir)