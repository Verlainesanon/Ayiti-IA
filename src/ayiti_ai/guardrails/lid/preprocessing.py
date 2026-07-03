import unicodedata
import regex
from ayiti_ai.guardrails.lid.schema import PreprocessedText

# Regex matching letters and combined marks (standard for word segmentation)
WORD_PATTERN = regex.compile(r"[\p{L}\p{M}]+", regex.UNICODE)

# Regex matching Latin characters (including extended/accented)
LATIN_PATTERN = regex.compile(r"\p{Latin}", regex.UNICODE)

# Regex matching ignorable characters like whitespace, punctuation, digits, symbols
IGNORABLE_PATTERN = regex.compile(r"[\p{Z}\p{P}\p{N}\p{S}\n\r\t]", regex.UNICODE)


def detect_script(text: str) -> str:
    """Detect if the script is primarily Latin.
    
    If more than 30% of non-ignorable characters are non-Latin, returns 'non-latin'.
    Otherwise, returns 'latin'.
    """
    total_len = len(text)
    if total_len == 0:
        return "latin"

    non_ignorable_chars = [c for c in text if not IGNORABLE_PATTERN.match(c)]
    if not non_ignorable_chars:
        return "latin"  # empty of real script characters (e.g. only emojis/numbers)

    non_latin_count = sum(1 for c in non_ignorable_chars if not LATIN_PATTERN.match(c))
    
    if (non_latin_count / len(non_ignorable_chars)) > 0.30:
        return "non-latin"
    
    return "latin"


def preprocess_text(text: str) -> PreprocessedText:
    """Preprocess the input text into a structured PreprocessedText object."""
    # 1. Unicode NFC Normalization
    normalized = unicodedata.normalize("NFC", text)
    
    # 2. Basic cleaning (strip leading/trailing space)
    cleaned = normalized.strip()
    
    # 3. Detect Script
    script = detect_script(cleaned)
    
    # 4. Tokenization
    tokens = WORD_PATTERN.findall(cleaned.lower())
    
    # 5. N-grams
    bigrams = [" ".join(tokens[i : i + 2]) for i in range(len(tokens) - 1)]
    trigrams = [" ".join(tokens[i : i + 3]) for i in range(len(tokens) - 2)]
    
    return PreprocessedText(
        original_text=text,
        normalized_text=cleaned,
        char_count=len(cleaned),
        word_count=len(tokens),
        script=script,
        tokens=tokens,
        bigrams=bigrams,
        trigrams=trigrams,
    )
