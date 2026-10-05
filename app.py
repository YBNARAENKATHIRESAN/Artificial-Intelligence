from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from telepathology_quality import run_analysis

st.set_page_config(page_title="Telepathology Image Quality", page_icon="🔬", layout="wide")

st.title("🔬 Telepathology Image Analysis Tool")
st.caption("Technical image-quality assessment only — not clinical diagnosis.")

uploaded = st.file_uploader(
    "Upload a pathology slide image",
    type=["jpg", "jpeg", "png", "bmp", "tif", "tiff"],
)

if uploaded is not None:
    with tempfile.TemporaryDirectory() as tmp:
        input_path = Path(tmp) / uploaded.name
        input_path.write_bytes(uploaded.getbuffer())
        output_dir = Path(tmp) / "outputs"

        try:
            report = run_analysis(str(input_path), str(output_dir), [95, 75, 50, 25])
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
            st.stop()

        status = report["quality_status"]
        if status.startswith("TECHNICALLY ACCEPTABLE"):
            st.success(status)
        else:
            st.warning(status)

        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Resolution",
            f'{report["resolution"]["width_px"]} × {report["resolution"]["height_px"]}',
        )
        col2.metric("Megapixels", report["resolution"]["megapixels"])
        col3.metric("Sharpness", report["sharpness"]["laplacian_variance"])

        st.subheader("Color analysis")
        color = report["color"]
        color_df = pd.DataFrame(
            {
                "Metric": [
                    "Mean Red",
                    "Mean Green",
                    "Mean Blue",
                    "Brightness",
                    "Saturation",
                ],
                "Value": [
                    color["mean_r"],
                    color["mean_g"],
                    color["mean_b"],
                    color["mean_brightness"],
                    color["mean_saturation"],
                ],
            }
        )
        st.dataframe(color_df, hide_index=True, use_container_width=True)
        st.image(str(output_dir / "rgb_histogram.png"), caption="RGB histogram")

        st.subheader("Compression experiment")
        compression_df = pd.DataFrame(report["compression"])
        st.dataframe(compression_df, hide_index=True, use_container_width=True)
        st.image(str(output_dir / "psnr_vs_quality.png"), caption="PSNR vs JPEG quality")
        st.image(str(output_dir / "filesize_vs_quality.png"), caption="File size vs JPEG quality")

        if report["quality_reasons"]:
            st.subheader("Quality flags")
            for reason in report["quality_reasons"]:
                st.write(f"• {reason}")

        st.download_button(
            "Download JSON report",
            data=(output_dir / "quality_report.json").read_bytes(),
            file_name="quality_report.json",
            mime="application/json",
        )
