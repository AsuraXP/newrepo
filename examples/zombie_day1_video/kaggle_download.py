# Paste this into a Kaggle notebook cell AFTER running run_video_kaggle.sh.
# It prints a clickable download link for the finished deliverable zip.
import os
from IPython.display import FileLink, display

ZIP = "/kaggle/working/out/zombie_day1_DELIVERABLE.zip"
assert os.path.exists(ZIP), f"not found: {ZIP} - run the pipeline cell first"
print(f"ready: {ZIP} ({os.path.getsize(ZIP)/1e6:.1f} MB)")
display(FileLink(ZIP))
