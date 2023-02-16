# %%
import os
import pandas as pd
import json
from pytube import YouTube
from moviepy.editor import *

root = "/home/vlso/Documents/GitHub/DMVR/examples"
os.chdir(root)


f = open("./youcook/youcookii_annotations_trainval.json")
data = json.load(f)
df = pd.DataFrame().from_dict(data["database"], "index")


def process_dataframe(
    df=df,
    subset="training",
    root="/home/vlso/Documents/GitHub/DMVR/examples/youcook/raw_videos/training",
):
    df = df.loc[df["subset"] == subset]
    df.drop(columns=["recipe_type", "subset", "duration"], inplace=True)
    objects = df["annotations"].values
    urls = df["video_url"].values
    dfs = []
    for i in range(len(objects)):
        temp_df = pd.DataFrame().from_dict(objects[i], "columns")
        temp_df["video_url"] = urls[i]
        dfs.append(temp_df)
    annotation_df = pd.concat(dfs)
    annotation_df[["start", "end"]] = annotation_df["segment"].tolist()
    annotation_df.drop(columns=["segment", "id"], inplace=True)
    annotation_df["video_path"] = annotation_df["video_url"].apply(
        lambda row: os.path.join(root, row.split("=")[-1] + ".mp4")
    )
    annotation_df.rename(columns={"sentence": "caption"}, inplace=True)
    header = ["video_path", "start", "end", "caption"]
    annotation_df.to_csv(
        "./youcook/csv_files/train_list.csv", columns=header, index=False
    )


def download_and_clip(failed_files, link, num_tries, resol, save_dir=""):
    # from time import process_time
    # t1_start = process_time()
    filename = os.path.join(save_dir, link.split("=")[-1] + ".mp4")
    if os.path.exists(filename):
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
                print(ys_aud[0])
                print(ys_vid[0])
            except:
                print("Error on download - trying again")
            else:
                break
        else:
            failed_files["pytube"] += [str(link.split("=")[-1])]
            return failed_files

        try:
            videoclip = VideoFileClip(f"{fname}_video.mp4")
            audioclip = AudioFileClip(f"{fname}_audio.mp4")
            clip = videoclip.set_audio(audioclip)
            clip.write_videofile(filename)
        except:
            failed_files["moviepy"] += [str(link.split("=")[-1])]

            print("error in moviepy")

        print("Download completed!!")
        os.remove(f"{fname}_audio.mp4")
        os.remove(f"{fname}_video.mp4")
    return failed_files
    # t1_stop = process_time()

    # print("Elapsed time:", t1_stop - t1_start)


# %%

# create csv file
process_dataframe()
# %%
# download video files
failed_files = {"pytube": [], "moviepy": []}
for link in df["video_url"]:
    download_and_clip(
        failed_files=failed_files,
        link=link,
        num_tries=1,
        resol="144p",
        save_dir="/home/vlso/Documents/GitHub/DMVR/examples/youcook/raw_videos/training",
    )
    print(failed_files)

# %%
download_and_clip(
    link="https://www.youtube.com/watch?v=-xbTvALWCIg",
    num_tries=2,
    resol="144p",
    save_dir="/home/vlso/Documents/GitHub/DMVR/examples/youcook/raw_videos/training",
)
# %%
input_csv = pd.read_csv(
    "/home/vlso/Documents/GitHub/DMVR/examples/youcook/csv_files/train_list.csv"
)
new_df = input_csv.loc[os.path.exists(input_csv["video_path"]) == True]

# %%
import os

input_csv_exists = input_csv[input_csv["video_path"].apply(os.path.exists)]
# %%
from pytube import YouTube

yt = YouTube("https://www.youtube.com/watch?v=-xbTvALWCIg")
yt2 = YouTube("https://www.youtube.com/watch?v=XOwypmUT5cc")
test = yt.streams
test2 = yt2.streams
# ys_aud = yt.streams.filter(progressive=True, file_extension="mp4").all()
# %%
ys_vid = yt.streams
# %%
ys_aud[0].download(filename=f"test_audio.mp4")
# %%
ys_aud[1].download(filename=f"test_video.mp4")

# %%
videoclip = VideoFileClip(f"test_video.mp4")
# %%
audioclip = AudioFileClip(f"test_audio.mp4")

# %%
clip = videoclip.set_audio(audioclip)

# %%
clip.write_videofile("test.mp4")

# %%
