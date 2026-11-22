from app.intelligence import canonicalize,fingerprint,topics_for,extractive_summary
def test_canonical_url_removes_tracking():
    assert canonicalize("HTTPS://Example.com/story/?utm_source=x&id=2")=="https://example.com/story?id=2"
def test_topics_and_summary():
    assert "technology" in topics_for("New AI software technology")
    assert extractive_summary("First sentence. Second sentence. Third sentence.")=="First sentence. Second sentence."
def test_fingerprint_is_stable():
    assert fingerprint("Hello!","World") == fingerprint("hello","world")
