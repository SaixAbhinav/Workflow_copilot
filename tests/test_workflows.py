from core.output_parser import extract_json, parse_output
from core.workflow_engine import merge_results
from input_processing.chunker import chunk_text
from input_processing.cleaner import clean_text

# ── chunker ─────────────────────────────────────────────────────────────────

def test_chunk_short_text_returns_single_chunk():
    text = "This is a short sentence."
    chunks = chunk_text(text, max_words=300)
    assert len(chunks) == 1
    assert chunks[0] == text

def test_chunk_splits_on_sentence_boundary():
    # 6 words per sentence × 10 sentences = 60 words; max_words=20 → 3 chunks
    sentences = ["Word one two three four five." for _ in range(10)]
    text = " ".join(sentences)
    chunks = chunk_text(text, max_words=20)
    assert len(chunks) > 1
    # No chunk should exceed max_words by more than one sentence
    for chunk in chunks:
        assert len(chunk.split()) <= 30  # one sentence overflow tolerance

def test_chunk_empty_string_returns_one_chunk():
    chunks = chunk_text("", max_words=300)
    assert len(chunks) == 1

def test_chunk_preserves_all_words():
    text = "Alpha beta gamma. Delta epsilon zeta. Eta theta iota kappa."
    original_words = set(text.split())
    all_chunk_words = set(" ".join(chunk_text(text, max_words=5)).split())
    assert original_words == all_chunk_words


# ── cleaner ──────────────────────────────────────────────────────────────────

def test_clean_normalises_whitespace():
    assert clean_text("hello   world") == "hello world"

def test_clean_strips_edges():
    assert clean_text("  hello  ") == "hello"

def test_clean_collapses_newlines():
    assert clean_text("line1\n\nline2") == "line1 line2"


# ── output_parser ────────────────────────────────────────────────────────────

def test_extract_json_simple():
    assert extract_json('{"key": "value"}') == '{"key": "value"}'

def test_extract_json_nested():
    raw = '{"a": {"b": 1}}'
    result = extract_json(raw)
    assert result == raw

def test_extract_json_strips_markdown_fence():
    raw = '```json\n{"key": "value"}\n```'
    assert extract_json(raw) == '{"key": "value"}'

def test_extract_json_returns_none_for_no_json():
    assert extract_json("no json here") is None

def test_parse_output_valid_json():
    result = parse_output('{"summary": "hello"}')
    assert result == {"summary": "hello"}

def test_parse_output_returns_error_on_invalid():
    result = parse_output("not json at all")
    assert "error" in result
    assert "raw" in result

def test_parse_output_handles_extra_text():
    raw = 'Here is the result: {"key_insights": ["a", "b"]}'
    result = parse_output(raw)
    assert result.get("key_insights") == ["a", "b"]


# ── merge_results ─────────────────────────────────────────────────────────────

def test_merge_tasks_combines_action_items():
    results = [
        {"action_items": [{"task": "A", "deadline": "Mon", "priority": "high"}]},
        {"action_items": [{"task": "B", "deadline": "Tue", "priority": "low"}]},
    ]
    merged = merge_results(results, "tasks")
    assert len(merged["action_items"]) == 2
    assert merged["action_items"][0]["task"] == "A"

def test_merge_insights_combines_key_insights():
    results = [
        {"key_insights": ["insight 1"]},
        {"key_insights": ["insight 2", "insight 3"]},
    ]
    merged = merge_results(results, "insights")
    assert merged["key_insights"] == ["insight 1", "insight 2", "insight 3"]

def test_merge_summary_concatenates_text():
    results = [
        {"summary": "Part one."},
        {"summary": "Part two."},
    ]
    merged = merge_results(results, "summary")
    assert "Part one." in merged["summary"]
    assert "Part two." in merged["summary"]
    # Summary workflow no longer emits key_insights.
    assert "key_insights" not in merged

def test_merge_empty_results_returns_empty_structure():
    merged = merge_results([], "tasks")
    assert merged == {"action_items": [], "source_type": None}

def test_merge_compare_combines_all_fields():
    results = [{
        "summary": "Two reports differ on budget.",
        "common_themes": ["growth"],
        "differences": ["budget figure"],
        "key_insights": ["Q4 critical"],
    }]
    merged = merge_results(results, "compare")
    assert merged["summary"] == "Two reports differ on budget."
    assert merged["common_themes"] == ["growth"]
    assert merged["differences"] == ["budget figure"]
    assert merged["key_insights"] == ["Q4 critical"]
