# %%
import subprocess


def streams(input_video):
    result = subprocess.run(
        ["ffmpeg", "-i", input_video], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    return result.stdout


# %%
res = streams(
    "/home/vlso/Documents/GitHub/DMVR/examples/UCF101/data/WallPushups/v_WallPushups_g01_c02.avi"
)


# %%
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


check = has_audio(
    "/home/vlso/Documents/GitHub/DMVR/examples/UCF101/data/Basketball/v_Basketball_g01_c01.avi"
)
# %%
