import csv
import io
import os
import urllib.request
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_CSV = os.path.join(BASE_DIR, "spam.csv")

UCI_ZIP_URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/rahulvasaikar/SMS-spam-Detection/master/SMSSpamCollection"


def parse_and_save(text):
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue

        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue

        label, message = parts
        label = label.strip().lower()
        message = message.strip()

        if label in ("ham", "spam") and message:
            rows.append((label, message))

    if len(rows) < 5000:
        raise ValueError(f"Dataset incomplete: only {len(rows)} messages found.")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["v1", "v2"])
        writer.writerows(rows)

    print(f"Done! Saved {len(rows)} messages to:")
    print(OUTPUT_CSV)


def download_from_uci():
    print("Downloading official UCI SMS Spam Collection...")
    with urllib.request.urlopen(UCI_ZIP_URL, timeout=60) as response:
        data = response.read()

    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = z.namelist()
        target = next(
            name for name in names
            if os.path.basename(name).lower() == "smsspamcollection"
        )
        raw = z.read(target)

    for encoding in ("utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass

    raise UnicodeDecodeError("Unable to decode dataset.")


def download_from_github():
    print("UCI download failed. Trying GitHub mirror...")
    with urllib.request.urlopen(GITHUB_RAW_URL, timeout=60) as response:
        raw = response.read()

    for encoding in ("utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass

    raise UnicodeDecodeError("Unable to decode dataset.")


def main():
    try:
        text = download_from_uci()
    except Exception as e:
        print("UCI error:", e)
        text = download_from_github()

    parse_and_save(text)


if __name__ == "__main__":
    main()
