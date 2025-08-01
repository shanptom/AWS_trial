import streamlit as st
import pandas as pd
import boto3
import json
import io
import zipfile
from datetime import datetime

# --- Streamlit + S3 setup ---
st.set_page_config(page_title="Microbiome Atlas", layout="wide")
st.title(" Microbiome Atlas")
st.markdown("Explore curated ASV-based microbiome datasets across diverse ecosystems and sequencing platforms.")

aws = st.secrets["aws"]
s3 = boto3.client(
    "s3",
    aws_access_key_id=aws["access_key"],
    aws_secret_access_key=aws["secret_key"],
    region_name=aws["region"]
)
BUCKET = aws["bucket"]

# --- Load project info from S3 ---
def get_all_projects():
    result = s3.list_objects_v2(Bucket=BUCKET, Delimiter='/')
    project_ids = [p['Prefix'].strip('/') for p in result.get('CommonPrefixes', [])]
    projects = []
    for pid in project_ids:
        try:
            key = f"{pid}/{pid}_info.json"
            obj = s3.get_object(Bucket=BUCKET, Key=key)
            data = json.loads(obj['Body'].read().decode('utf-8'))
            projects.append({
                "Project ID": pid,
                "Title": data.get("title", "Untitled"),
                "Gene": data.get("gene", "NA"),
                "Platform": data.get("instrument", "NA"),
                "Environment": data.get("sample_type", "NA"),
                "Samples": data.get("samples", 0),
                "Uploaded": data.get("timestamp", "NA")
            })
        except:
            continue
    return pd.DataFrame(projects)

df = get_all_projects()

# --- Filter UI ---
st.subheader(" Explore Public Datasets")
with st.expander(" Apply Filters"):
    filters = {}
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.checkbox("Filter by Gene"):
            filters["Gene"] = st.selectbox("Gene", sorted(df["Gene"].unique()))
    with col2:
        if st.checkbox("Filter by Environment"):
            filters["Environment"] = st.selectbox("Environment", sorted(df["Environment"].unique()))
    with col3:
        if st.checkbox("Filter by Platform"):
            filters["Platform"] = st.selectbox("Platform", sorted(df["Platform"].unique()))

filtered_df = df.copy()
for col, val in filters.items():
    filtered_df = filtered_df[filtered_df[col] == val]

# --- Display table with checkboxes ---
st.markdown("###  Available Datasets")
selected_projects = []
cols = st.columns([1, 4, 3, 2, 2, 2])

with cols[0]:
    st.markdown("**Select**")
with cols[1]:
    st.markdown("**Project ID**")
with cols[2]:
    st.markdown("**Title**")
with cols[3]:
    st.markdown("**Gene**")
with cols[4]:
    st.markdown("**Platform**")
with cols[5]:
    st.markdown("**Environment**")

for idx, row in filtered_df.iterrows():
    c = st.columns([1, 4, 3, 2, 2, 2])
    with c[0]:
        checked = st.checkbox("", key=f"row_{row['Project ID']}")
    if checked:
        selected_projects.append(row["Project ID"])
    c[1].write(row["Project ID"])
    c[2].write(row["Title"])
    c[3].write(row["Gene"])
    c[4].write(row["Platform"])
    c[5].write(row["Environment"])

# --- ZIP Download ---
if selected_projects:
    if st.button(" Download Selected Projects as ZIP"):
        try:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for project_id in selected_projects:
                    prefix = f"{project_id}/"
                    expected_files = [
                        f"{project_id}_count.csv",
                        f"{project_id}_taxa.csv",
                        f"{project_id}_meta.csv",
                        f"{project_id}_asv.fasta",
                        f"{project_id}_info.json"
                    ]
                    for fname in expected_files:
                        s3_key = prefix + fname
                        obj = s3.get_object(Bucket=BUCKET, Key=s3_key)
                        content = obj['Body'].read()
                        zipf.writestr(f"{project_id}/{fname}", content)

            zip_buffer.seek(0)
            st.download_button(
                label=" Click to download ZIP",
                data=zip_buffer,
                file_name="microbiome_datasets.zip",
                mime="application/zip"
            )
        except Exception as e:
            st.error(f"Error creating ZIP: {e}")

# --- Upload prompt ---
with st.expander(" Are you submitting data?"):
    st.markdown("""
    You can upload your microbiome dataset (count table, taxonomy, metadata, and FASTA) directly to the Atlas.

     Required files: `count.csv`, `taxa.csv`, `meta.csv`, `asv.fasta`  
     Use our [metadata template](#)  
     A project ID will be assigned automatically.

     Please use the **Upload** tab in the sidebar to get started.
    """)

# --- Footer ---
st.divider()
st.markdown("""
 2025 Microbiome Atlas    
""")
