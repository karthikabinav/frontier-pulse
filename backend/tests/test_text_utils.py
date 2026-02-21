from app.services.text_utils import make_chunks, strip_reference_tail


def test_strip_reference_tail_truncates_reference_section() -> None:
    text = "Intro\nMain findings\nReferences\n[1] x"
    assert strip_reference_tail(text) == "Intro\nMain findings"


def test_make_chunks_respects_overlap_and_target() -> None:
    text = "Introduction\n" + ("token " * 800)
    chunks = make_chunks(text, target_tokens=200, overlap_tokens=20)
    assert len(chunks) >= 2
    assert all(chunk.estimated_tokens > 0 for chunk in chunks)
