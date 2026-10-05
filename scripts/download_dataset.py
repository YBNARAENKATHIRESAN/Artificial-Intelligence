from __future__ import annotations

import argparse
from pathlib import Path

from datasets import load_dataset

LABEL_NAMES = {
    0: "ADIPOSE",
    1: "COMPLEX",
    2: "DEBRIS",
    3: "EMPTY",
    4: "LYMPHO",
    5: "MUCOSA",
    6: "STROMA",
    7: "TUMOR",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a reproducible subset of Kather Texture 2016."
    )
    parser.add_argument(
        "--per-class",
        type=int,
        default=10,
        help="Images to save per class (default: 10).",
    )
    parser.add_argument("--output", type=Path, default=Path("data/kather2016"))
    args = parser.parse_args()

    if args.per_class < 1:
        raise SystemExit("--per-class must be at least 1.")

    ds = load_dataset("YueFanXia/Kather-texture-2016", split="train")
    args.output.mkdir(parents=True, exist_ok=True)

    counts = {name: 0 for name in LABEL_NAMES.values()}
    saved = 0

    for row in ds:
        label_id = int(row["label"])
        if label_id not in LABEL_NAMES:
            continue

        label_name = LABEL_NAMES[label_id]
        if counts[label_name] >= args.per_class:
            continue

        class_dir = args.output / label_name
        class_dir.mkdir(parents=True, exist_ok=True)
        image = row["image"].convert("RGB")
        filename = class_dir / f"{label_name.lower()}_{counts[label_name]:03d}.png"
        image.save(filename)
        counts[label_name] += 1
        saved += 1

        if all(v >= args.per_class for v in counts.values()):
            break

    print(f"Saved {saved} images to {args.output}")
    for label, count in counts.items():
        print(f"{label}: {count}")


if __name__ == "__main__":
    main()
