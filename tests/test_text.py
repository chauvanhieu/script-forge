from sflib.text import clusters, display_text, invalid_tags, norm, tokens, uses_clusters


def test_invalid_tags_allows_supported_markup_only():
    ok = "Wait [pause] then [pause 500ms] and [pause 1.5s] [laughter] [sigh] [[gif|jiff]]."
    assert invalid_tags(ok) == []
    assert invalid_tags("She is [excited] now") == ["[excited]"]
    assert invalid_tags("Say [[Nuh-VAD-uh]]") == ["[[Nuh-VAD-uh]]"]


def test_display_text_strips_tags_and_keeps_written_half():
    assert display_text("Hello [laughter], [[gif|jiff]] fans [pause 300ms] !") == "Hello, gif fans!"
    assert display_text("No. [sigh] Not again.") == "No. Not again."


def test_tokens_for_spaced_language():
    assert tokens("Xin chào [sigh] các bạn.", "vi") == ["Xin", "chào", "các", "bạn."]


def test_tokens_for_cluster_language_attach_punctuation():
    assert uses_clusters("zh-Hans")
    assert not uses_clusters("en-US")
    assert tokens("你好，世界", "zh") == ["你", "好，", "世", "界"]


def test_clusters_keep_combining_marks_with_their_base():
    assert clusters("กิน") == ["กิ", "น"]


def test_norm_removes_punctuation_and_case():
    assert norm("Bạn.") == "bạn"
    assert norm("“Hello,”") == "hello"
