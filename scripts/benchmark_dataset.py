from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from telepathology_quality import run_analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark the quality tool on real histopathology images.")
    parser.add_argument("--data", type=Path, default=Path("data/kather2016"))
    parser.add_argument("--output", type=Path, default=Path("results/dataset_benchmark"))
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    rows = []

    images = sorted(args.data.glob("**/*.png"))
    if not images:
        raise SystemExit("No dataset images found. Run scripts/download_dataset.py first.")

    for image_path in images:
        out_dir = args.output / image_path.stem
        report = run_analysis(str(image_path), str(out_dir), qualities=[95, 75, 50, 25])
        rows.append(
            {
                "file": image_path.name,
                "class": image_path.parent.name,
                "width": report["resolution"]["width_px"],
                "height": report["resolution"]["height_px"],
                "megapixels": report["resolution"]["megapixels"],
                "mean_r": report["color"]["mean_r"],
                "mean_g": report["color"]["mean_g"],
                "mean_b": report["color"]["mean_b"],
                "brightness": report["color"]["mean_brightness"],
                "saturation": report["color"]["mean_saturation"],
                "sharpness": report["sharpness"]["laplacian_variance"],
                "status": report["quality_status"],
                "source_file_bytes": report["source_file_bytes"],
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(args.output / "benchmark_results.csv", index=False)

    summary = (
        df.groupby("class")
        .agg(
            images=("file", "count"),
            mean_sharpness=("sharpness", "mean"),
            mean_brightness=("brightness", "mean"),
            mean_saturation=("saturation", "mean"),
            mean_file_size=("source_file_bytes", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(args.output / "class_summary.csv", index=False)

    plt.figure(figsize=(8, 5))
    df.boxplot(column="sharpness", by="class", rot=45)
    plt.suptitle("")
    plt.title("Sharpness Distribution by Kather 2016 Tissue Class")
    plt.xlabel("Tissue class")
    plt.ylabel("Laplacian variance")
    plt.tight_layout()
    plt.savefig(args.output / "sharpness_by_class.png", dpi=160)
    plt.close()

    stats = {
        "images_analyzed": int(len(df)),
        "classes": sorted(df["class"].unique().tolist()),
        "mean_sharpness": float(df["sharpness"].mean()),
        "min_sharpness": float(df["sharpness"].min()),
        "max_sharpness": float(df["sharpness"].max()),
        "mean_file_size_bytes": float(df["source_file_bytes"].mean()),
    }
    (args.output / "benchmark_summary.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
