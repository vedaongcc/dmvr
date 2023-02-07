import argparse
import pandas as pd
import subprocess


# Construct the argument parser
parser = argparse.ArgumentParser()

# Add the arguments to the parser
parser.add_argument(
    "-path",
    required=True,
    help="path to the text file containing a list of video files",
)
parser.add_argument("-fname", required=True, help="name of the output csv file")
args = parser.parse_args()


in_file = pd.read_csv(
    args.path,
    names=["video_path"],
)
in_file = in_file.replace({"^\s*|\s*$": ""}, regex=True)
in_file["video_path"] = in_file["video_path"].apply(lambda row: row.split(" ")[0])

root = "/home/vlso/Documents/GitHub/DMVR/examples/UCF101/data"


def has_audio(filename):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=nb_streams",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return int(result.stdout) - 1


def get_length(filename):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return float(result.stdout)


df_hasAudio = pd.DataFrame(columns=["video_path", "has_aud"])

import os.path as osp

df_hasAudio["video_path"] = in_file["video_path"].apply(lambda row: osp.join(root, row))
df_hasAudio["has_aud"] = df_hasAudio["video_path"].apply(lambda row: has_audio(row))

has_aud = df_hasAudio["video_path"].loc[df_hasAudio["has_aud"] == 1]

df = pd.DataFrame(columns=["video_path", "start", "end", "label", "caption"])
df["video_path"] = has_aud
df["start"] = 0
df["end"] = df["video_path"].apply(lambda row: int(get_length(row.strip())))
df["label"] = in_file["video_path"].apply(lambda row: row.split("/")[0])
df["caption"] = "test"


folder = "csvs_vid" if "splits_vid" in args.path else "csvs_audvid"
df.to_csv(osp.join(folder, args.fname), index=False)
