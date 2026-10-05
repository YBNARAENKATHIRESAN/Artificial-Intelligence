# Telepathology Image Analysis Tool

A student mini-project that uses **Python and OpenCV** to assess the **technical quality** of pathology slide images before remote viewing or transmission.

> **Important:** This prototype does not diagnose disease and does not determine clinical suitability for diagnosis. It measures technical image properties only.

## Features

- Resolution analysis: width, height, megapixels
- Color analysis: mean RGB, brightness and saturation
- Sharpness analysis: variance of the Laplacian
- JPEG compression experiment at multiple quality factors
- MSE, PSNR, compression ratio and file-size comparison
- RGB histogram
- PSNR-vs-quality and file-size-vs-quality graphs
- JSON and CSV output for documentation and report writing

## Architecture

```text
Pathology Slide Image
        |
        v
Image Input (OpenCV)
        |
        +------------------+-------------------+
        |                  |                   |
        v                  v                   v
Resolution             Color              Sharpness
Analysis               Analysis           Analysis
        |                  |                   |
        +------------------+-------------------+
                           |
                           v
                  JPEG Compression Tests
                  Q=95 / 75 / 50 / 25
                           |
                  +--------+--------+
                  |                 |
                  v                 v
                 PSNR              MSE
                  |                 |
                  +--------+--------+
                           v
                Results + Graphs + Report
```

## Run locally

```bash
pip install -r requirements.txt
python telepathology_quality.py path/to/pathology_image.jpg
```

Outputs are written to `outputs/`.

## Run in Google Colab

1. Upload the project files to Colab.
2. Install dependencies:

```python
!pip install -r requirements.txt
```

3. Upload a pathology image:

```python
from google.colab import files
files.upload()
```

4. Execute:

```python
!python telepathology_quality.py your_image.jpg
```

## Generated outputs

- `quality_report.json` — complete numerical report
- `compression_results.csv` — compression experiment table
- `rgb_histogram.png` — RGB distribution graph
- `psnr_vs_quality.png` — quality/compression graph
- `filesize_vs_quality.png` — file-size graph
- `compressed/` — JPEG test images

## Suggested test cases

| Test case | Input | Purpose |
|---|---|---|
| TC1 | High-resolution slide | Check resolution and baseline color/quality |
| TC2 | Low-resolution copy | Demonstrate resolution limitation |
| TC3 | JPEG Q95 | Low compression / high quality |
| TC4 | JPEG Q50 | Medium compression |
| TC5 | JPEG Q25 | High compression |
| TC6 | Intentionally blurred image | Demonstrate sharpness measurement |

## Analysis

Expected engineering trend:

- Lower JPEG quality usually reduces file size.
- Stronger JPEG compression can increase distortion and reduce PSNR.
- Sharpness score is content-dependent, so it should be treated as an indicator rather than a universal clinical threshold.
- Color statistics can help detect major image appearance changes, but they are not stain-validation or diagnosis algorithms.

## Limitations

- No clinical validation.
- No whole-slide-image (WSI) pyramid/tiling support in this student prototype.
- JPEG is a lossy format, so PSNR/MSE depend on the original image and chosen compression settings.
- Sharpness is content-dependent.
- No scanner-specific calibration or stain normalization.

## Future enhancement

- WSI support (SVS/TIFF/OME-TIFF)
- More robust focus/artifact metrics
- Stain normalization
- Scanner-specific calibration
- Interactive web dashboard
- Network transmission simulation
- Automated PDF report

## Assignment coverage

This repository directly supports the mini-project requirements for:

- system architecture/block diagram
- problem definition
- hardware/software requirements
- data flow and communication process
- implementation
- test cases and results
- graphs/tables
- analysis
- limitations
- future enhancement
- conclusion
