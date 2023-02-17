# %%
import os
import pandas as pd
import json
import numpy as np

root = "/home/vlso/Documents/GitHub/DMVR/examples"
os.chdir(root)

## Create dataframe from json containing metadata (video links and text associations)

f = open("./youcook2/annotations/youcookii_annotations_trainval.json")
data = json.load(f)
df = pd.DataFrame().from_dict(data["database"], "index")

save_path = "/home/vlso/Drives/p/P41xx/P4161_Olympic_Stadium/Misc/Heysham_PBS176/pretrain/Data/youcook2_data"
csv_path = "./youcook2/csv_files/test.csv"


# %%
def process_dataframe(df=df, subset="training", root_path=save_path, csv_path=csv_path):
    df = df.loc[df["subset"] == subset]
    df.drop(columns=["recipe_type", "subset", "duration"], inplace=True)
    objects = df["annotations"].values
    urls = df["video_url"].values
    df.to_csv("./youcook2/csv_files/links.csv")
    dfs = []
    for i in range(len(objects)):
        temp_df = pd.DataFrame().from_dict(objects[i], "columns")
        temp_df["video_url"] = urls[i]
        dfs.append(temp_df)
    annotation_df = pd.concat(dfs)
    annotation_df[["start", "end"]] = annotation_df["segment"].tolist()
    annotation_df.drop(columns=["segment", "id"], inplace=True)
    annotation_df["video_path"] = annotation_df["video_url"].apply(
        lambda row: os.path.join(root_path, row.split("=")[-1] + ".mp4")
    )
    annotation_df.rename(columns={"sentence": "caption"}, inplace=True)
    header = ["video_path", "start", "end", "caption"]
    annotation_df.to_csv(csv_path, columns=header, index=False)


process_dataframe()

# %%
