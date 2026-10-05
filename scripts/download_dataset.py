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
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-class", type=int, default=10)
    parser.add_argument("--output", type=Path, default=Path("data/kather2016"))
    args = parser.parse_args()

    ds = load_dataset("YueFanXia/Kather-texture-2016", split="train")
    args.output.mkdir(parents=True, exist_ok=True)

    counts = {name: 0 for name in LABEL_NAMES.values()}

    for row in ds:
        label = LABEL_NAMES[int(row["label"])]
        if counts[label] >= args.per_class:
            continue
        out_dir = args.output / label
        out_dir.mkdir(parents=True, exist_ok=True)
        image = row["image"].convert("RGB")
        image.save(out_dir / f"{label.lower()}_{counts[label]:03d}.png")
        counts[label] += 1
        if all(v >= args.per_class for v in counts.values()):
            break

    print(f"Saved to {args.output}")
    for label, count in counts.items():
        print(f"{label}: {count}")

if __name__ == "__main__":
    main()
