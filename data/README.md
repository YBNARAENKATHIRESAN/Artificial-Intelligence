# Real Histopathology Dataset

## Kather Texture 2016

This project uses the **Kather Texture 2016** colorectal histology dataset for real-data validation.

- 5,000 RGB histological images
- 150 × 150 pixels
- 8 tissue categories
- H&E-stained human colorectal adenocarcinoma tissue
- Images digitized with an Aperio ScanScope at 20× magnification
- Samples anonymized
- License: CC BY 4.0
- Official Zenodo record: https://doi.org/10.5281/zenodo.53169
- Hugging Face mirror: https://huggingface.co/datasets/YueFanXia/Kather-texture-2016

The full dataset is not committed here because of its size. Use `scripts/download_dataset.py` to obtain a reproducible subset.

Classes: ADIPOSE, COMPLEX, DEBRIS, EMPTY, LYMPHO, MUCOSA, STROMA, TUMOR.
