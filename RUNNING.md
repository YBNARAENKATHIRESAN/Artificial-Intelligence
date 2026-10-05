# Running the Telepathology Tool

## Local command-line mode

```bash
pip install -r requirements.txt
python telepathology_quality.py path/to/pathology_image.jpg
```

## Local dashboard

```bash
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal, upload a pathology image, and view resolution, color, sharpness, compression, PSNR, MSE, graphs, and the downloadable JSON report.

## Google Colab

Upload `telepathology_quality.py`, `requirements.txt`, and a pathology image.

```python
!pip install -r requirements.txt
!python telepathology_quality.py your_image.jpg
```

The command creates `outputs/quality_report.json`, `outputs/compression_results.csv`, and the requested graphs/compressed images.
