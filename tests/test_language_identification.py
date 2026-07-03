import pytest
from ayiti_ai.guardrails.lid.preprocessing import preprocess_text, detect_script
from ayiti_ai.guardrails.lid.levels.level1_rules import Level1Rules


def test_detect_script():
    # Latin texts
    assert detect_script("Hello world") == "latin"
    assert detect_script("Bonjour tout le monde") == "latin"
    assert detect_script("Kijan ou ye?") == "latin"
    assert detect_script("Fèk vini bòkò lakou") == "latin"
    
    # Non-Latin texts
    assert detect_script("안녕하세요") == "non-latin"
    assert detect_script("Привет, как дела?") == "non-latin"
    assert detect_script("مرحبا كيف حالك") == "non-latin"
    
    # Text with mixed symbols / punctuation
    assert detect_script("12345 !!! ??? 😊") == "latin"  # empty of script letters, defaults to latin


def test_preprocessing():
    # Test normalization & counts
    text = "Mwen ap manje nan lakou a."
    context = preprocess_text(text)
    
    assert context.original_text == text
    assert context.normalized_text == text.strip()
    assert context.char_count == len(text.strip())
    assert context.word_count == 6
    assert context.script == "latin"
    
    # Check tokens
    assert context.tokens == ["mwen", "ap", "manje", "nan", "lakou", "a"]
    
    # Check n-grams
    assert "mwen ap" in context.bigrams
    assert "mwen ap manje" in context.trigrams


def test_preprocessing_contractions():
    # Haitian Creole contractions
    c1 = preprocess_text("M'ap manje")
    assert c1.tokens == ["m", "ap", "manje"]
    
    c2 = preprocess_text("L'ale nan mache")
    assert c2.tokens == ["l", "ale", "nan", "mache"]
    
    c3 = preprocess_text("Sa w ap fè?")
    assert c3.tokens == ["sa", "w", "ap", "fè"]
    
    # French contractions
    c4 = preprocess_text("C'est bon")
    assert c4.tokens == ["c", "est", "bon"]
    
    # English contractions
    c5 = preprocess_text("John's book")
    assert c5.tokens == ["john", "s", "book"]


def test_level1_rules_matching():
    # Initialize level 1 rules (uses default config/lid_markers.yaml)
    rules = Level1Rules()
    rules.warmup()
    
    # Haitian Creole
    ctx_ht1 = preprocess_text("Mwen ap manje nan lakou a.")
    res_ht1 = rules.predict(ctx_ht1.normalized_text, ctx_ht1)
    assert res_ht1.matched is True
    assert res_ht1.language == "ht"
    assert res_ht1.confidence == 1.0
    
    ctx_ht2 = preprocess_text("M'ap chèche paske m gen bezwen")
    res_ht2 = rules.predict(ctx_ht2.normalized_text, ctx_ht2)
    assert res_ht2.matched is True
    assert res_ht2.language == "ht"
    
    # French
    ctx_fr1 = preprocess_text("C'est très bon, j'aime beaucoup ça.")
    res_fr1 = rules.predict(ctx_fr1.normalized_text, ctx_fr1)
    assert res_fr1.matched is True
    assert res_fr1.language == "fr"
    assert res_fr1.confidence == 1.0
    
    ctx_fr2 = preprocess_text("Où sont passés les enfants?")
    res_fr2 = rules.predict(ctx_fr2.normalized_text, ctx_fr2)
    assert res_fr2.matched is True
    assert res_fr2.language == "fr"

    # English
    ctx_en1 = preprocess_text("The cat is on the mat.")
    res_en1 = rules.predict(ctx_en1.normalized_text, ctx_en1)
    assert res_en1.matched is True
    assert res_en1.language == "en"
    assert res_en1.confidence == 1.0

    # Short / Ambiguous - should not match (delegates to Level 2)
    ctx_amb = preprocess_text("OK")
    res_amb = rules.predict(ctx_amb.normalized_text, ctx_amb)
    assert res_amb.matched is False
    
    ctx_amb2 = preprocess_text("salut")
    res_amb2 = rules.predict(ctx_amb2.normalized_text, ctx_amb2)
    assert res_amb2.matched is False


def test_level2_fasttext():
    """
    Tests Level 2 (FastText lid.176.ftz) detection.
    Uses longer sentences for reliable detection — the .ftz compressed model
    has lower per-token confidence than .bin, so sentences < 10 words may not 
    score high enough to cross the 0.40 threshold.
    """
    from ayiti_ai.guardrails.lid.levels.level2_fasttext import Level2FastText
    
    fasttext_level = Level2FastText()
    fasttext_level.warmup()
    
    # Haitian Creole - longer sentence for reliable detection with .ftz
    ctx_ht = preprocess_text(
        "Mwen rele Jean, m ap travay nan lekol la epi m pral al nan mache a apre midi."
    )
    res_ht = fasttext_level.predict(ctx_ht.normalized_text, ctx_ht)
    assert res_ht.matched is True, f"Expected HT match, got: {res_ht.evidence}"
    assert res_ht.language == "ht", f"Expected 'ht', got: {res_ht.language}"
    assert res_ht.confidence >= 0.30, f"Expected confidence >= 0.30, got: {res_ht.confidence}"
    
    # French - works well even on short sentences
    ctx_fr = preprocess_text(
        "Bonjour, comment allez-vous aujourd'hui? Je suis tres content de vous voir."
    )
    res_fr = fasttext_level.predict(ctx_fr.normalized_text, ctx_fr)
    assert res_fr.matched is True, f"Expected FR match, got: {res_fr.evidence}"
    assert res_fr.language == "fr", f"Expected 'fr', got: {res_fr.language}"
    assert res_fr.confidence >= 0.80
    
    # English - works well even on short sentences
    ctx_en = preprocess_text(
        "Hello how are you doing today? I hope everything is going well for you."
    )
    res_en = fasttext_level.predict(ctx_en.normalized_text, ctx_en)
    assert res_en.matched is True, f"Expected EN match, got: {res_en.evidence}"
    assert res_en.language == "en", f"Expected 'en', got: {res_en.language}"
    assert res_en.confidence >= 0.80


def test_robust_lid_pipeline_integration():
    """Integration test: full pipeline RobustLID Levels 1+2."""
    from ayiti_ai.guardrails.lid.pipeline import RobustLID

    lid = RobustLID()
    lid.warmup()

    # HT — should be caught by Level 1 (deterministic markers)
    res_ht = lid.detect("Mwen ap manje nan lakou a, tout moun ap pale toujou.")
    assert res_ht.primary_language == "ht"
    assert res_ht.level_used == 1  # Level 1 should catch this
    assert res_ht.confidence == 1.0

    # FR — should be caught by Level 1 (c'est, qu', beaucoup)
    res_fr = lid.detect("C'est très bien, je suis heureux de vous voir aujourd'hui.")
    assert res_fr.primary_language == "fr"
    assert res_fr.level_used == 1

    # EN — should be caught by Level 1 (the, is)
    res_en = lid.detect("The cat is sitting on the mat and is very comfortable.")
    assert res_en.primary_language == "en"
    assert res_en.level_used == 1

    # Short ambiguous — should fall through to Level 2 at minimum
    res_amb = lid.detect("Bonjou zanmi, koman ou ye?")
    assert res_amb.primary_language in ["ht", "fr", "unknown"]

    # Non-latin — should return unknown
    res_arabic = lid.detect("مرحبا كيف حالك اليوم")
    assert res_arabic.primary_language == "unknown"
    assert "non_latin_script_detected" in res_arabic.warnings

    # Cache test — second call should return same result
    res_ht_2 = lid.detect("Mwen ap manje nan lakou a, tout moun ap pale toujou.")
    assert res_ht_2.primary_language == res_ht.primary_language

