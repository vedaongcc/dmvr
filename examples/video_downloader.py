import os
import argparse
from pytube import YouTube
from moviepy.editor import *
import shutil
import csv

# if directory does not exists - maybe make directory
parser = argparse.ArgumentParser()


parser.add_argument(
    "--csv_path", type=str, help="path to csv containing youtube video links"
)
parser.add_argument(
    "--failed_files", type=str, help="path to csv to save failed files to"
)
parser.add_argument(
    "--save_dir",
    type=str,
    help="local path to where the mp4 files should be saved temporarily during download",
)
parser.add_argument(
    "--dest_dir",
    type=str,
    help="path on the p-drive to where the raw mp4 video-audio files should be saved permanently",
)

parser.add_argument(
    "--num_tries", type=int, help="number of times to retry a failed download"
)
parser.add_argument(
    "--resolution", type=str, help="resolution of the videos to retrieve from youtube"
)
args = parser.parse_args()


def get_streams(link, resol, fname):
    yt = YouTube(link)
    ys_aud = yt.streams.filter(only_audio=True, file_extension="mp4").all()
    ys_vid = yt.streams.filter(only_video=True, file_extension="mp4", res=resol).all()
    print("Downloading...")
    ys_aud[0].download(filename=f"{fname}_audio.mp4")
    ys_vid[0].download(filename=f"{fname}_video.mp4")


def merge_vid_aud(fname, save_fname, dest_fname):
    videoclip = VideoFileClip(f"{fname}_video.mp4")
    audioclip = AudioFileClip(f"{fname}_audio.mp4")
    clip = videoclip.set_audio(audioclip)
    clip.write_videofile(save_fname)
    shutil.move(save_fname, dest_fname)


def download(failed_files, link, num_tries, resol, save_dir="", dest_dir=""):
    save_fname = os.path.join(save_dir, link.split("=")[-1] + ".mp4")
    dest_fname = os.path.join(dest_dir, link.split("=")[-1] + ".mp4")
    if os.path.exists(dest_fname):
        print("file exists")
    else:
        fname = link.split("=")[-1]
        print(fname, save_fname, dest_fname)

        for i in range(num_tries):
            try:
                get_streams(link, resol, fname)
            except:
                print("Error on download - trying again")
            else:
                break
        else:
            failed_files["pytube"] += [str(link.split("=")[-1])]
            if os.path.exists(f"{fname}_audio.mp4"):
                os.remove(f"{fname}_audio.mp4")
            if os.path.exists(f"{fname}_video.mp4"):
                os.remove(f"{fname}_video.mp4")

            return failed_files

        try:
            merge_vid_aud(fname, save_fname, dest_fname)
            print("Download completed!!")

        except:
            failed_files["moviepy"] += [str(link.split("=")[-1])]

            print("error in moviepy")

        os.remove(f"{fname}_audio.mp4")
        os.remove(f"{fname}_video.mp4")

    return failed_files


def run():
    def flatten(l):
        return [item for sublist in l for item in sublist]

    file = open(args.csv_path, "r")
    links = flatten(list(csv.reader(file, delimiter=",")))
    file.close()

    failed_files = {"pytube": [], "moviepy": []}
    for link in links:
        download(
            failed_files=failed_files,
            link=link,
            num_tries=args.num_tries,
            resol=args.resolution,
            save_dir=args.save_dir,
            dest_dir=args.dest_dir,
        )

    fails = csv.writer(open(args.failed_files, "w"))

    for key, val in failed_files.items():
        fails.writerow([key, val])


run()
