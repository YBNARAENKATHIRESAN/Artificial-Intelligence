from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_image(path: str | Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image


def analyze_resolution(image: np.ndarray) -> dict[str, Any]:
    height, width = image.shape[:2]
    return {
        "width_px": int(width),
        "height_px": int(height),
        "megapixels": round((width * height) / 1_000_000, 4),
        "channels": int(image.shape[2]) if image.ndim == 3 else 1,
    }


def analyze_color(image: np.ndarray) -> dict[str, Any]:
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return {
        "mean_r": round(float(rgb[..., 0].mean()), 4),
        "mean_g": round(float(rgb[..., 1].mean()), 4),
        "mean_b": round(float(rgb[..., 2].mean()), 4),
        "mean_brightness": round(float(hsv[..., 2].mean()), 4),
        "mean_saturation": round(float(hsv[..., 1].mean()), 4),
    }


def analyze_sharpness(image: np.ndarray) -> dict[str, Any]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    return {"laplacian_variance": round(score, 4)}


def psnr(original: np.ndarray, compressed: np.ndarray) -> float:
    a = original.astype(np.float32)
    b = compressed.astype(np.float32)
    mse = float(np.mean((a - b) ** 2))
    if mse == 0:
        return float("inf")
    return float(10 * np.log10((255.0 ** 2) / mse))


def compression_experiment(
    image: np.ndarray,
    original_file_size: int,
    output_dir: Path,
    qualities: list[int],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for quality in qualities:
        output_path = output_dir / f"compressed_q{quality}.jpg"
        ok = cv2.imwrite(
            str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, int(quality)]
        )
        if not ok:
            raise RuntimeError(f"Could not write {output_path}")

        compressed = cv2.imread(str(output_path), cv2.IMREAD_COLOR)
        if compressed is None:
            raise RuntimeError(f"Could not reopen {output_path}")

        size = output_path.stat().st_size
        value = psnr(image, compressed)
        rows.append(
            {
                "jpeg_quality": quality,
                "file_size_bytes": int(size),
                "compression_ratio": round(original_file_size / size, 4) if size else None,
                "mse": round(
                    float(
                        np.mean(
                            (
                                image.astype(np.float32)
                                - compressed.astype(np.float32)
                            )
                            ** 2
                        )
                    ),
                    6,
                ),
                "psnr_db": round(value, 4) if np.isfinite(value) else None,
            }
        )

    return pd.DataFrame(rows)


def save_color_histogram(image: np.ndarray, path: Path) -> None:
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 5))
    for idx, label in enumerate(("Red", "Green", "Blue")):
        plt.hist(rgb[..., idx].ravel(), bins=256, alpha=0.45, label=label)
    plt.xlabel("Pixel intensity")
    plt.ylabel("Frequency")
    plt.title("RGB Color Histogram")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def save_compression_graphs(df: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.plot(df["jpeg_quality"], df["psnr_db"], marker="o")
    plt.xlabel("JPEG quality")
    plt.ylabel("PSNR (dB)")
    plt.title("Image Quality vs JPEG Quality")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_dir / "psnr_vs_quality.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(df["jpeg_quality"], df["file_size_bytes"], marker="o")
    plt.xlabel("JPEG quality")
    plt.ylabel("File size (bytes)")
    plt.title("File Size vs JPEG Quality")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_dir / "filesize_vs_quality.png", dpi=160)
    plt.close()


def build_quality_status(
    resolution: dict[str, Any],
    color: dict[str, Any],
    sharpness: dict[str, Any],
    compression: pd.DataFrame,
) -> tuple[str, list[str]]:
    reasons: list[str] = []

    if resolution["width_px"] < 512 or resolution["height_px"] < 512:
        reasons.append("low pixel dimensions")
    if sharpness["laplacian_variance"] < 50:
        reasons.append("low sharpness score")
    if color["mean_saturation"] < 15:
        reasons.append("low color saturation")
    if not compression.empty and compression["psnr_db"].iloc[0] is not None:
        if float(compression["psnr_db"].iloc[0]) < 30:
            reasons.append("noticeable distortion even at JPEG Q=95")

    return ("REVIEW REQUIRED" if reasons else "TECHNICALLY ACCEPTABLE (PROTOTYPE)"), reasons


def run_analysis(input_path: str, output_root: str, qualities: list[int]) -> dict[str, Any]:
    image = load_image(input_path)
    input_file = Path(input_path)
    output_dir = Path(output_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    source_file_size = input_file.stat().st_size

    resolution = analyze_resolution(image)
    color = analyze_color(image)
    sharpness = analyze_sharpness(image)
    compression = compression_experiment(
        image,
        source_file_size,
        output_dir / "compressed",
        qualities,
    )
    save_color_histogram(image, output_dir / "rgb_histogram.png")
    save_compression_graphs(compression, output_dir)

    status, reasons = build_quality_status(resolution, color, sharpness, compression)

    report = {
        "project": "Telepathology Image Analysis Tool",
        "scope": "Technical image-quality assessment only; not clinical diagnosis.",
        "input_file": input_file.name,
        "source_file_bytes": int(source_file_size),
        "resolution": resolution,
        "color": color,
        "sharpness": sharpness,
        "compression": compression.to_dict(orient="records"),
        "quality_status": status,
        "quality_reasons": reasons,
        "artifacts": [
            "rgb_histogram.png",
            "psnr_vs_quality.png",
            "filesize_vs_quality.png",
        ],
    }

    with open(output_dir / "quality_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    compression.to_csv(output_dir / "compression_results.csv", index=False)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Telepathology image technical-quality analysis using Python/OpenCV."
    )
    parser.add_argument("image", help="Path to a pathology slide image")
    parser.add_argument(
        "--output",
        default="outputs",
        help="Output directory (default: outputs)",
    )
    parser.add_argument(
        "--qualities",
        nargs="+",
        type=int,
        default=[95, 75, 50, 25],
        help="JPEG quality factors to test",
    )
    args = parser.parse_args()

    if any(q < 1 or q > 100 for q in args.qualities):
        raise SystemExit("JPEG quality values must be between 1 and 100.")

    report = run_analysis(args.image, args.output, args.qualities)
    print(json.dumps(report, indent=2))
    print(f"\nSaved results to: {os.path.abspath(args.output)}")


if __name__ == "__main__":
    main()
