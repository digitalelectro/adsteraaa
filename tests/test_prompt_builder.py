from prompt_builder import PromptRequest, build_prompt_text, SIZE_PRESETS


def test_build_prompt_text_includes_context_and_style():
    request = PromptRequest(
        paragraph="The king discovers the enemy's secret tunnel into the fortress.",
        style_instructions="cinematic, moody, volumetric light",
        extra_context="Ancient battle documentary",
    )

    prompt = build_prompt_text(request)

    assert "visual for a narrated video script" in prompt
    assert "Paragraph:" in prompt
    assert request.paragraph in prompt
    assert request.style_instructions in prompt
    assert request.extra_context in prompt


def test_size_presets_cover_requested_aspects():
    for label in ["1:1", "4:3", "3:4", "16:9", "9:16"]:
        assert label in SIZE_PRESETS
        width, height = SIZE_PRESETS[label]
        assert width > 0 and height > 0
