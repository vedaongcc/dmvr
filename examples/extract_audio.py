

#%%
import ffmpeg
import numpy as np
def extract_audio(
    video_path: str, start: float, end: float, sampling_rate: int = 48000
):
    """Extract raw mono audio float list from video_path with ffmpeg."""
    cmd = ffmpeg.input(video_path, ss=start, t=end - start).output(
        "pipe:", ac=1, ar=sampling_rate, format="s32le"
    )
    audio, _ = cmd.run(capture_stdout=True, quiet=True, capture_stderr=True)
    audio = np.frombuffer(audio, np.float32)
    return list(audio)


test = extract_audio('/home/vlso/Documents/GitHub/DMVR/examples/UCF101/UCF101/data/Basketball/v_Basketball_g01_c01.avi',
0,4,48000)
# %%
test2 = extract_audio('/home/vlso/Documents/GitHub/DMVR/examples/UCF101/UCF101/data/CleanAndJerk/v_CleanAndJerk_g01_c01.avi', 0, 6, 48000)
# %%
