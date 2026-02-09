from app.sanitizer import sanitize_url, is_long_url


def test_sanitize_url_valid():
    assert sanitize_url("https://example.com") == "https://example.com"


def test_sanitize_url_adds_https():
    assert sanitize_url("example.com").startswith("https://")


def test_sanitize_url_empty():
    assert sanitize_url("") == ""


def test_sanitize_url_removes_dangerous_schemes():
    assert sanitize_url("javascript:alert(1)") == ""


def test_is_long_url_true_for_very_long_urls():
    long_path = "a" * 300
    url = f"https://example.com/{long_path}"
    assert is_long_url(url) is True


def test_is_long_url_false_for_normal_urls():
    assert is_long_url("https://example.com") is False

