# Copyright 2021 DeepMind Technologies Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Python script to generate TFRecords of SequenceExample from raw videos."""
# %%
import contextlib
import math
import os
from typing import Dict, Optional, Sequence

from absl import app
from absl import flags
import ffmpeg
import numpy as np
import pandas as pd
import tensorflow as tf

"""
flags.DEFINE_string("csv_path", None, "Input csv")
flags.DEFINE_string("output_path", None, "Tfrecords output path.")
flags.DEFINE_string(
    "video_root_path", None, "Root directory containing the raw videos."
)
flags.DEFINE_integer(
    "num_shards",
    -1,
    "Number of shards to output, -1 means"
    "it will automatically adapt to the sqrt(num_examples).",
)
flags.DEFINE_bool("decode_audio", False, "Whether or not to decode the audio")
flags.DEFINE_bool("shuffle_csv", False, "Whether or not to shuffle the csv.")
FLAGS = flags.FLAGS
"""

_JPEG_HEADER = b"\xff\xd8"


@contextlib.contextmanager
def _close_on_exit(writers):
    """Call close on all writers on exit."""
    try:
        yield writers
    finally:
        for writer in writers:
            writer.close()


def add_float_list(
    key: str, values: Sequence[float], sequence: tf.train.SequenceExample
):
    sequence.feature_lists.feature_list[key].feature.add().float_list.value[:] = values


def add_bytes_list(
    key: str, values: Sequence[bytes], sequence: tf.train.SequenceExample
):
    sequence.feature_lists.feature_list[key].feature.add().bytes_list.value[:] = values


def add_int_list(key: str, values: Sequence[int], sequence: tf.train.SequenceExample):
    sequence.feature_lists.feature_list[key].feature.add().int64_list.value[:] = values


def set_context_int_list(
    key: str, value: Sequence[int], sequence: tf.train.SequenceExample
):
    sequence.context.feature[key].int64_list.value[:] = value


def set_context_bytes(key: str, value: bytes, sequence: tf.train.SequenceExample):
    sequence.context.feature[key].bytes_list.value[:] = (value,)


def set_context_float(key: str, value: float, sequence: tf.train.SequenceExample):
    sequence.context.feature[key].float_list.value[:] = (value,)


def set_context_int(key: str, value: int, sequence: tf.train.SequenceExample):
    sequence.context.feature[key].int64_list.value[:] = (value,)


def extract_frames(
    video_path: str, start: float, end: float, fps: int = 10, min_resize: int = 256
):
    """Extract list of jpeg bytes from video_path using ffmpeg."""
    new_width = "(iw/min(iw,ih))*{}".format(min_resize)
    cmd = (
        ffmpeg.input(video_path)
        .trim(start=start, end=end)
        .filter("fps", fps=fps)
        .filter("scale", new_width, -1)
        .output("pipe:", format="image2pipe")
    )
    jpeg_bytes, _ = cmd.run(capture_stdout=True, quiet=True)
    jpeg_bytes = jpeg_bytes.split(_JPEG_HEADER)[1:]
    jpeg_bytes = map(lambda x: _JPEG_HEADER + x, jpeg_bytes)
    return list(jpeg_bytes)


def extract_audio(
    video_path: str, start: float, end: float, sampling_rate: int = 48000
):
    """Extract raw mono audio float list from video_path with ffmpeg."""
    cmd = ffmpeg.input(video_path, ss=start, t=end - start).output(
        "pipe:", ac=1, ar=sampling_rate, format="s32le"
    )

    audio, _ = cmd.run(capture_stdout=True, quiet=True)

    audio = np.frombuffer(audio, np.float32)
    return list(audio)


# %%

video_path = "/home/vlso/Documents/GitHub/DMVR/examples/UCF101/data/ApplyEyeMakeup/v_ApplyEyeMakeup_g01_c01.avi"
imgs_encoded = extract_frames(video_path, 0, 6)
seq_example = tf.train.SequenceExample()
caption = "test caption"
set_context_bytes("caption/string", caption.encode(), seq_example)


# %%


def generate_sequence_example(
    video_path: str,
    start: float,
    end: float,
    label_name: Optional[str] = None,
    caption: Optional[str] = None,
    label_map: Optional[Dict[str, int]] = None,
):
    """Generate a sequence example."""
    video_path = video_path
    imgs_encoded = extract_frames(video_path, start, end)

    # Initiate the sequence example.
    seq_example = tf.train.SequenceExample()

    # Add the label list as text and indices.
    if label_name:
        set_context_int("clip/label/index", label_map[label_name], seq_example)
        set_context_bytes("clip/label/text", label_name.encode(), seq_example)
    if caption:
        set_context_bytes("caption/string", caption.encode(), seq_example)
    # Add the frames as one feature per frame.
    for img_encoded in imgs_encoded:
        add_bytes_list("image/encoded", [img_encoded], seq_example)
    # Add audio.

    audio = extract_audio(video_path, start, end)
    add_float_list("WAVEFORM/feature/floats", audio, seq_example)

    # Add other metadata.
    set_context_bytes("video/filename", video_path.encode(), seq_example)
    # Add start and time in micro seconds.
    set_context_int("clip/start/timestamp", int(1000000 * start), seq_example)
    set_context_int("clip/end/timestamp", int(1000000 * end), seq_example)

    return seq_example


unique_labels = ["ApplyEyeMakeup", "testlabel"]
l_map = {unique_labels[i]: i for i in range(len(unique_labels))}
test = generate_sequence_example(
    "/home/vlso/Documents/GitHub/DMVR/examples/UCF101/data/ApplyEyeMakeup/v_ApplyEyeMakeup_g01_c01.avi",
    0,
    6,
    "ApplyEyeMakeup",
    "test caption",
)
# %%
from generate_from_file import generate_sequence_example

l_map = {
    "CricketShot": 0,
    "StillRings": 1,
    "Hammering": 2,
    "Rafting": 3,
    "BodyWeightSquats": 4,
    "Haircut": 5,
    "FrisbeeCatch": 6,
    "ShavingBeard": 7,
    "PlayingFlute": 8,
    "CliffDiving": 9,
    "LongJump": 10,
    "BoxingSpeedBag": 11,
    "TableTennisShot": 12,
    "BrushingTeeth": 13,
    "SkyDiving": 14,
    "SoccerPenalty": 15,
    "UnevenBars": 16,
    "PlayingDhol": 17,
    "Surfing": 18,
    "Archery": 19,
    "PlayingCello": 20,
    "ApplyEyeMakeup": 21,
    "Shotput": 22,
    "Bowling": 23,
    "Typing": 24,
    "MoppingFloor": 25,
    "HandstandPushups": 26,
    "WallPushups": 27,
    "HammerThrow": 28,
    "HeadMassage": 29,
    "FieldHockeyPenalty": 30,
    "HandstandWalking": 31,
    "PlayingDaf": 32,
    "BabyCrawling": 33,
    "IceDancing": 34,
    "CuttingInKitchen": 35,
    "ParallelBars": 36,
    "WritingOnBoard": 37,
    "CricketBowling": 38,
    "SumoWrestling": 39,
    "BandMarching": 40,
    "BlowDryHair": 41,
    "BlowingCandles": 42,
    "BoxingPunchingBag": 43,
    "FrontCrawl": 44,
    "Knitting": 45,
    "BasketballDunk": 46,
    "ApplyLipstick": 47,
    "BalanceBeam": 48,
    "FloorGymnastics": 49,
    "PlayingSitar": 50,
}
seq_ex = generate_sequence_example(
    "/home/vlso/Documents/GitHub/DMVR/examples/UCF101/data/BabyCrawling/v_BabyCrawling_g02_c01.avi",
    0,
    4,
    "BabyCrawling",
    "test",
    l_map,
)

# %%
