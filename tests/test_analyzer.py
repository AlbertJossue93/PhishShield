from app.analyzer import URL_Analyzer


def test_analyzer_https_ok():
    analyzer = URL_Analyzer("https://example.com")
    analyzer.check_https_and_ssl()
    assert "✅ URL usa HTTPS" in analyzer.feedback
    assert analyzer.score == 0


def test_analyzer_http_increases_score():
    analyzer = URL_Analyzer("http://example.com")
    analyzer.check_https_and_ssl()
    # Deve marcar que não usa HTTPS e aumentar o score
    assert any("não usa HTTPS" in msg for msg in analyzer.feedback)
    assert analyzer.score >= 1


def test_analyzer_length_checks():
    short = URL_Analyzer("https://ex.com")
    short.check_length()
    assert any("tamanho normal" in msg for msg in short.feedback)

    long = URL_Analyzer("https://example.com/" + "a" * 130)
    long.check_length()
    assert any("URL muito longa" in msg for msg in long.feedback)

