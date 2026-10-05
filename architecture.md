# System Architecture and Data Flow

## Problem definition

Telepathology requires digital pathology images to be technically usable for remote viewing. This project checks measurable image properties before transmission, focusing on resolution, color, sharpness and compression behavior.

## Software requirements

- Python 3.10+
- OpenCV
- NumPy
- Pandas
- Matplotlib
- Google Colab or a local Python environment

## Hardware requirements

- Any modern laptop/desktop
- 4 GB RAM or more recommended
- Storage for slide images and generated outputs
- Scanner/camera is optional; the prototype works from existing image files

## Data flow

```text
Input image
   |
   v
OpenCV decode
   |
   +--> Resolution metrics
   |
   +--> RGB/HSV color metrics
   |
   +--> Grayscale + Laplacian variance
   |
   +--> JPEG compression at selected qualities
             |
             +--> file size
             +--> compression ratio
             +--> MSE
             +--> PSNR
   |
   v
CSV + JSON + graphs
   |
   v
Technical quality summary
```

## Boundary of the system

The output is a **technical quality assessment**, not a medical diagnosis and not a claim that an image is clinically sufficient for diagnosis.
