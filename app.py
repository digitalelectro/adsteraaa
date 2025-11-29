"""Streamlit UI for generating image prompts and images via Vertex AI.

Features:
- Upload a JSON list of timestamped lines (start, end, text) or paste text.
- Choose segment length and automatically assign lines to segments using
  ``segmenter.build_segments``.
- Provide a global style instruction so every prompt shares the same look.
- Choose output aspect ratio for images.
- Generate prompts with Gemini and images with the Vertex image model.

This UI focuses on clarity for non-Python users while keeping the underlying
pipeline explicit and auditable.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

import streamlit as st

from prompt_builder import SIZE_PRESETS
from segmenter import build_segments
from vertex_client import VertexConfig, generate_image_prompt, generate_images


st.set_page_config(page_title="Script-to-Image Prompts", layout="wide")
st.title("Script segmenting, prompt generation, and image creation")


@st.cache_data(show_spinner=False)
def parse_lines(raw: str) -> List[dict]:
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("Input must be a JSON list of objects with start, end, text.")
    return data


default_project_id = os.getenv("PROJECT_ID", "")
default_location = os.getenv("LOCATION", "us-central1")
default_sa_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")


with st.sidebar:
    st.header("Vertex AI configuration")
    project_id = st.text_input(
        "Project ID",
        placeholder="my-gcp-project",
        value=default_project_id,
    )
    location = st.text_input("Region", value=default_location)
    service_account_path = st.text_input(
        "Service account JSON path (optional)",
        value=default_sa_path,
        help="If left blank, GOOGLE_APPLICATION_CREDENTIALS will be used.",
    )
    st.divider()
    style_instructions = st.text_area(
        "Global visual style",
        value="dramatic lighting, painterly, high detail",
        help="These style notes will be appended to EVERY prompt so the visuals stay consistent.",
    )
    aspect_label = st.selectbox("Image size (aspect ratio)", list(SIZE_PRESETS.keys()), index=3)


st.subheader("1) Load timestamped script lines")
uploaded = st.file_uploader("Upload JSON (list of {start, end, text})", type=["json"])
lines_text = st.text_area("...or paste JSON here", height=200)

if uploaded:
    raw_text = uploaded.read().decode("utf-8")
elif lines_text.strip():
    raw_text = lines_text
else:
    raw_text = ""

lines = []
if raw_text:
    try:
        lines = parse_lines(raw_text)
        st.success(f"Loaded {len(lines)} lines")
    except Exception as exc:  # noqa: BLE001 - surfaced to user for clarity
        st.error(f"Could not parse input: {exc}")


st.subheader("2) Segment and generate prompts")
segment_length = st.number_input("Segment length (seconds)", value=30.0, min_value=5.0, step=5.0)

generated_prompts = []
segments = []

if st.button("Build segments and generate prompts", disabled=not lines or not project_id.strip()):
    with st.spinner("Building segments and calling Gemini..."):
        segments = build_segments(lines, segment_length=segment_length)
        config = VertexConfig(
            project_id=project_id.strip(),
            location=location.strip(),
            service_account_json=Path(service_account_path) if service_account_path.strip() else None,
        )
        for segment in segments:
            prompt = generate_image_prompt(
                paragraph=segment.text,
                style_instructions=style_instructions,
                config=config,
                extra_context=f"Segment {segment.index} covering {segment.start:.1f}–{segment.end:.1f}s",
            )
            generated_prompts.append({"segment": segment.index, "prompt": prompt})

    if generated_prompts:
        st.success(f"Generated {len(generated_prompts)} prompts")

if generated_prompts:
    st.write("Review prompts (you can copy these directly into the image generator):")
    for item in generated_prompts:
        st.markdown(f"**Segment {item['segment']}**")
        st.code(item["prompt"], language="markdown")


st.subheader("3) Generate images")
if generated_prompts:
    if st.button("Generate images with Vertex", disabled=not project_id.strip()):
        with st.spinner("Generating images..."):
            config = VertexConfig(
                project_id=project_id.strip(),
                location=location.strip(),
                service_account_json=Path(service_account_path) if service_account_path.strip() else None,
            )
            prompts_only = [item["prompt"] for item in generated_prompts]
            images = generate_images(prompts_only, size_label=aspect_label, config=config)
        st.success(f"Created {len(images)} images")
        for idx, image in enumerate(images):
            st.image(image._image_bytes, caption=f"Image {idx + 1} ({aspect_label})")  # noqa: SLF001
else:
    st.info("Generate prompts first to enable image generation.")


st.subheader("Deployment help")
st.markdown(
    """
    - Install dependencies: `pip install streamlit google-cloud-aiplatform vertexai`.
    - Provide credentials: set `GOOGLE_APPLICATION_CREDENTIALS` to your service account JSON
      **or** enter the path in the sidebar field.
    - Run locally: `streamlit run app.py` and open the displayed URL.
    - On Vercel/Render/etc.: add the same dependencies and set environment variables for
      `GOOGLE_APPLICATION_CREDENTIALS`, `PROJECT_ID`, and `LOCATION` (you can map them to the
      sidebar defaults).
    - Ensure your service account has the Vertex AI User role to access both text and image models.
    """
)

