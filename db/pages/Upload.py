import streamlit as st
import pandas as pd
import boto3
import io
import json
from datetime import datetime

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Upload Dataset", layout="centered")
st.title(" Upload Your Dataset")

# --- S3 Setup ---
aws = st.secrets["aws"]
s3 = boto3.client(
    "s3",
    aws_access_key_id=aws["access_key"],
    aws_secret_access_key=aws["secret_key"],
    region_name=aws["region"]
)
BUCKET = aws["bucket"]

# --- Required Metadata Columns ---
REQUIRED_META_COLS = [
    "#SampleID", "Instrument", "Library", "Gene", "Region",
    "PrimerF", "PrimerR", "Latitude", "Longitude", "Date",
    "Time", "SampleType", "Country"
]

# --- User Instructions ---
st.markdown("""
Please upload the following **4 files**:
- `count.csv`
- `taxa.csv`
- `meta.csv` (must contain required columns)
- `asv.fasta`

Also, provide a short **project title** (e.g., Mangrove Sediment Microbiome).
""")

# --- Project Title ---
title = st.text_input(" Project Title", max_chars=100)

# --- Upload Files ---
uploaded_files = st.file_uploader(
    "Upload your 4 files here",
    accept_multiple_files=True,
    type=['csv', 'fasta']
)

# --- Start validation after all 4 files are uploaded ---
if uploaded_files:
    if len(uploaded_files) != 4:
        st.warning(" Please upload exactly 4 files.")
    elif not title:
        st.warning(" Please enter a project title.")
    else:
        # Identify uploaded files
        count_file = next((f for f in uploaded_files if f.name.endswith("count.csv")), None)
        taxa_file = next((f for f in uploaded_files if f.name.endswith("taxa.csv")), None)
        meta_file = next((f for f in uploaded_files if f.name.endswith("meta.csv")), None)
        fasta_file = next((f for f in uploaded_files if f.name.endswith(".fasta")), None)

        if not all([count_file, taxa_file, meta_file, fasta_file]):
            st.error(" Missing one or more required files: count.csv, taxa.csv, meta.csv, asv.fasta")
        else:
            try:
                # --- Read and validate metadata ---
                meta_df = pd.read_csv(meta_file)
                missing_cols = [col for col in REQUIRED_META_COLS if col not in meta_df.columns]
                if missing_cols:
                    st.error(f" Metadata file is missing required columns: {', '.join(missing_cols)}")
                else:
                    # --- Generate new project ID ---
                    existing = s3.list_objects_v2(Bucket=BUCKET, Delimiter='/')
                    used_ids = [p['Prefix'].strip('/').upper() for p in existing.get('CommonPrefixes', [])]
                    i = 1
                    while f"PRJ{i:03}" in used_ids:
                        i += 1
                    project_id = f"PRJ{i:03}"
                    folder = f"{project_id}/"

                    # --- Safe extractor for metadata values ---
                    def safe_extract(col_name):
                        try:
                            values = meta_df[col_name].dropna().unique()
                            return values[0] if len(values) > 0 else "NA"
                        except:
                            return "NA"

                    # --- Build info.json content ---
                    info = {
                        "title": title,
                        "instrument": safe_extract("Instrument"),
                        "gene": safe_extract("Gene"),
                        "region": safe_extract("Region"),
                        "country": safe_extract("Country"),
                        "sample_type": safe_extract("SampleType"),
                        "samples": meta_df.shape[0],
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }

                    # --- Upload files to S3 ---
                    file_map = {
                        f"{project_id}_count.csv": count_file,
                        f"{project_id}_taxa.csv": taxa_file,
                        f"{project_id}_meta.csv": meta_file,
                        f"{project_id}_asv.fasta": fasta_file
                    }

                    for fname, file in file_map.items():
                        s3.upload_fileobj(file, BUCKET, folder + fname)

                    # --- Upload info.json to S3 ---
                    s3.put_object(
                        Bucket=BUCKET,
                        Key=f"{folder}{project_id}_info.json",
                        Body=json.dumps(info, indent=2),
                        ContentType="application/json"
                    )

                    # --- Success Message ---
                    st.success(f" Upload complete! Your project ID is **{project_id}**")
                    st.markdown("You can now view this project in the **Explore** tab.")
                    st.code(json.dumps(info, indent=2), language="json")

            except Exception as e:
                st.error(f" Upload failed: {e}")
