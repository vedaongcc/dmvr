# %%
import os
from pytube import YouTube
from moviepy.editor import *
import shutil

root = "/home/vlso/Documents/GitHub/DMVR/examples"
os.chdir(root)


def download_and_clip(failed_files, link, num_tries, resol, save_dir="", dest_dir=""):
    save_fname = os.path.join(save_dir, link.split("=")[-1] + ".mp4")
    dest_fname = os.path.join(dest_dir, link.split("=")[-1] + ".mp4")
    if os.path.exists(dest_fname):
        print("file exists")
    else:
        fname = link.split("=")[-1]
        for i in range(num_tries):
            try:
                yt = YouTube(link)
                ys_aud = yt.streams.filter(only_audio=True, file_extension="mp4").all()
                ys_vid = yt.streams.filter(
                    only_video=True, file_extension="mp4", res=resol
                ).all()
                print("Downloading...")
                ys_aud[0].download(filename=f"{fname}_audio.mp4")
                ys_vid[0].download(filename=f"{fname}_video.mp4")
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
            videoclip = VideoFileClip(f"{fname}_video.mp4")
            audioclip = AudioFileClip(f"{fname}_audio.mp4")
            clip = videoclip.set_audio(audioclip)
            clip.write_videofile(save_fname)
            shutil.move(save_fname, dest_fname)
        except:
            failed_files["moviepy"] += [str(link.split("=")[-1])]

            print("error in moviepy")

        print("Download completed!!")
        os.remove(f"{fname}_audio.mp4")
        os.remove(f"{fname}_video.mp4")

    return failed_files


# %%
import pandas as pd

csv_path = "./youcook2/csv_files/test.csv"
df = pd.read_csv("./youcook2/csv_files/links.csv")

# %%
# download video files
failed_files = {"pytube": [], "moviepy": []}
for link in df["video_url"]:
    download_and_clip(
        failed_files=failed_files,
        link=link,
        num_tries=1,
        resol="144p",
        save_dir="/home/vlso/Documents/GitHub/DMVR/examples/youcook2/raw_videos",
        dest_dir="/home/vlso/Drives/p/P41xx/P4161_Olympic_Stadium/Misc/Heysham_PBS176/pretrain/Data/youcook2_data",
    )
    print(failed_files)

# %%
