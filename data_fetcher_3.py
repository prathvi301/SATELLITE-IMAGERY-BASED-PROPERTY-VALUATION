import time
import requests
import pandas as pd
from pathlib import Path
MAPBOX_TOKEN = "api key here"

IMAGE_SIZE = "400x400"
ZOOM_LEVEL = 17
MAP_STYLE = "satellite-v9"

SLEEP_TIME = 0.15  # seconds

BASE_URL = "https://api.mapbox.com/styles/v1/mapbox"
PROJECT_ROOT = Path.cwd()

IMAGE_DIR = PROJECT_ROOT / "data" / "images"
LOG_DIR = PROJECT_ROOT / "data" / "logs"

TRAIN_IMAGE_DIR = IMAGE_DIR / "train"
TEST_IMAGE_DIR = IMAGE_DIR / "test"

LOG_FILE = LOG_DIR / "image_download_log.csv"

# Create folders
for d in [IMAGE_DIR, TRAIN_IMAGE_DIR, TEST_IMAGE_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)
def construct_mapbox_url(lat, lon):
    return (
        f"{BASE_URL}/{MAP_STYLE}/static/"
        f"{lon},{lat},{ZOOM_LEVEL}/"
        f"{IMAGE_SIZE}"
        f"?access_token={MAPBOX_TOKEN}"
    )


def download_image(url, save_path):
    try:
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(r.content)
            return True, ""

        return False, f"HTTP {r.status_code}"

    except Exception as e:
        return False, str(e)


def load_log():
    if LOG_FILE.exists():
        return pd.read_csv(LOG_FILE)
    return pd.DataFrame(columns=["id", "split", "status", "filename", "error"])


def append_log(log_df, record):
    log_df.loc[len(log_df)] = record
    log_df.to_csv(LOG_FILE, index=False)

def process_dataset(csv_path, split):

    print(f"\nDownloading {split.upper()} images...")
    df = pd.read_csv(csv_path)

    required_cols = {"id", "lat", "long"}
    if not required_cols.issubset(df.columns):
        raise ValueError("CSV must have columns: id, lat, long")

    image_dir = TRAIN_IMAGE_DIR if split == "train" else TEST_IMAGE_DIR
    log_df = load_log()
    done = set(log_df["id"].astype(str))

    total = len(df)
    success = failed = 0

    for idx, row in df.iterrows():
        prop_id = str(row["id"])

        if prop_id in done:
            continue

        lat, lon = row["lat"], row["long"]
        image_path = image_dir / f"{prop_id}.png"

        url = construct_mapbox_url(lat, lon)
        ok, error = download_image(url, image_path)

        append_log(
            log_df,
            {
                "id": prop_id,
                "split": split,
                "status": "success" if ok else "failed",
                "filename": image_path.name,
                "error": error,
            },
        )

        success += int(ok)
        failed += int(not ok)

        if idx % 100 == 0:
            print(f"{idx}/{total} processed...")

        time.sleep(SLEEP_TIME)

    print(f"\n{split.upper()} DONE | Success: {success} | Failed: {failed}")

# RETRY FAILED DOWNLOADS
def retry_failed():

    log_df = load_log()

    # normalize ID to string
    log_df["id"] = log_df["id"].astype(str)

    failed = log_df[log_df["status"] == "failed"]

    if failed.empty:
        print("\n🎉 No failed downloads to retry.")
        return

    print(f"\n🔁 Retrying {len(failed)} failed downloads...\n")

    for _, row in failed.iterrows():
        prop_id = str(row["id"])
        split = row["split"]

        csv = TRAIN_CSV_PATH if split == "train" else TEST_CSV_PATH
        df = pd.read_csv(csv)

        df["id"] = df["id"].astype(str)

        rec = df[df["id"] == prop_id]
        if rec.empty:
            continue

        lat = rec.iloc[0]["lat"]
        lon = rec.iloc[0]["long"]

        image_dir = TRAIN_IMAGE_DIR if split == "train" else TEST_IMAGE_DIR
        image_path = image_dir / f"{prop_id}.png"

        url = construct_mapbox_url(lat, lon)
        ok, error = download_image(url, image_path)

       
        mask = log_df["id"] == prop_id
        log_df.loc[mask, "status"] = "success" if ok else "failed"
        log_df.loc[mask, "error"] = error

        log_df.to_csv(LOG_FILE, index=False)

        print(f"{prop_id}: {'✅ FIXED' if ok else '❌ STILL FAILING'}")

    print("\n✔ Retry complete")

if __name__ == "__main__":

    BASE_DIR = Path(__file__).parent

    TRAIN_CSV_PATH = BASE_DIR / "train.csv"
    TEST_CSV_PATH = BASE_DIR / "test.csv"

    process_dataset(TRAIN_CSV_PATH, "train")
    process_dataset(TEST_CSV_PATH, "test")

    retry_failed()

    print("\nAll downloads completed.")