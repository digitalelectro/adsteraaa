"""Utilities for building clear LLM prompts for image generation.

These helpers ensure the model knows:
- The paragraph comes from a narrated video script.
- It should output a concise image-generation prompt focused on the visuals
  that match that paragraph.
- Optional *style instructions* are appended so every generated image shares a
  consistent look.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# Supported aspect ratios for downstream image generation.
SIZE_PRESETS = {
    "1:1": (1024, 1024),
    "4:3": (1152, 864),
    "3:4": (864, 1152),
    "16:9": (1344, 756),
    "9:16": (756, 1344),
}


@dataclass
class PromptRequest:
    """Inputs needed to build an LLM request for an image prompt."""

    paragraph: str
    style_instructions: str = ""
    extra_context: Optional[str] = None


def build_prompt_text(request: PromptRequest) -> str:
    """Return an instruction string for the LLM to generate an image prompt.

    The text explicitly tells the LLM that the paragraph belongs to a script and
    that the output must be a single image-generation prompt (not narration or
    dialogue). Style requirements are appended verbatim so they are propagated to
    every prompt.
    """

    base_instruction = (
        "You are creating a visual for a narrated video script. Given the"
        " paragraph below, write ONE concise, vivid image-generation prompt"
        " that depicts the visuals for that paragraph. Avoid narration,"
        " dialogue, or camera movement notes. Keep it grounded to the"
        " paragraph's content."
    )

    context = f"Additional context: {request.extra_context}" if request.extra_context else ""
    style_clause = (
        f"Apply this consistent visual style to the entire prompt: {request.style_instructions.strip()}"
        if request.style_instructions.strip()
        else ""
    )

    return "\n\n".join(
        part
        for part in [
            base_instruction,
            context,
            "Paragraph:",
            request.paragraph.strip(),
            style_clause,
        ]
        if part
    )


__all__ = ["PromptRequest", "build_prompt_text", "SIZE_PRESETS"]
