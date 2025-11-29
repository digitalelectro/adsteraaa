"""Google Vertex AI helpers for text (LLM) and image generation.

The functions here expect Vertex AI credentials to be available via
``GOOGLE_APPLICATION_CREDENTIALS`` or an explicit service account JSON path.
They keep imports inside functions so the rest of the project (and tests) can
run without the Vertex dependencies installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from prompt_builder import PromptRequest, build_prompt_text, SIZE_PRESETS


@dataclass
class VertexConfig:
    project_id: str
    location: str
    service_account_json: Optional[Path] = None
    text_model: str = "gemini-1.5-pro-002"
    image_model: str = "imagegeneration@006"


def _init_vertex(config: VertexConfig) -> None:
    import vertexai
    from google.oauth2 import service_account

    kwargs = {"project": config.project_id, "location": config.location}
    if config.service_account_json:
        kwargs["credentials"] = service_account.Credentials.from_service_account_file(
            config.service_account_json
        )
    vertexai.init(**kwargs)


def generate_image_prompt(paragraph: str, style_instructions: str, config: VertexConfig, *, extra_context: str | None = None) -> str:
    """Generate a single image prompt for the paragraph using Gemini."""

    from vertexai.generative_models import GenerativeModel

    _init_vertex(config)
    request = PromptRequest(
        paragraph=paragraph,
        style_instructions=style_instructions,
        extra_context=extra_context,
    )
    prompt_text = build_prompt_text(request)
    model = GenerativeModel(config.text_model)
    response = model.generate_content(
        prompt_text,
        generation_config={"temperature": 0.4, "max_output_tokens": 400},
    )
    return response.text.strip()


def generate_images(prompts: Iterable[str], *, size_label: str, config: VertexConfig, seed: int | None = None) -> list:
    """Generate images for each prompt using the Vertex image generation model.

    The ``size_label`` must match a key in ``SIZE_PRESETS`` (e.g., "16:9").
    """

    from vertexai.preview.vision_models import ImageGenerationModel

    _init_vertex(config)
    if size_label not in SIZE_PRESETS:
        raise ValueError(f"Unsupported size '{size_label}'. Choose one of: {', '.join(SIZE_PRESETS)}")

    width, height = SIZE_PRESETS[size_label]
    model = ImageGenerationModel.from_pretrained(config.image_model)

    images = []
    for prompt in prompts:
        result = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            guidance_scale=15,
            seed=seed,
            size=f"{width}x{height}",
            safety_filter_level="block_most",
        )
        images.extend(result.images)
    return images


__all__ = [
    "VertexConfig",
    "generate_image_prompt",
    "generate_images",
]
