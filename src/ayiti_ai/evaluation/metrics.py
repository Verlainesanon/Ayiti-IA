"""
Module d'évaluation pour Ayiti-AI.

Calcule les métriques BLEU, ROUGE et perplexité pour évaluer
la qualité du modèle, notamment en créole haïtien.
"""
import logging
import math
from typing import Dict, List, Optional

import torch

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# BLEU
# ---------------------------------------------------------------------------

def compute_bleu(predictions: List[str], references: List[str]) -> Dict[str, float]:
    """
    Calcule le score BLEU (sacrebleu) entre prédictions et références.

    Args:
        predictions: Liste de textes générés par le modèle.
        references: Liste de textes de référence (gold).

    Returns:
        Dict avec 'bleu' (score 0-100) et 'bp' (brevity penalty).
    """
    try:
        from sacrebleu.metrics import BLEU
    except ImportError:
        raise ImportError("Installez sacrebleu: pip install sacrebleu")

    metric = BLEU(effective_order=True)
    result = metric.corpus_score(predictions, [references])
    return {
        "bleu": round(result.score, 4),
        "bp": round(result.bp, 4),
        "ratio": round(result.sys_len / result.ref_len, 4) if result.ref_len else 0.0,
    }


# ---------------------------------------------------------------------------
# ROUGE
# ---------------------------------------------------------------------------

def compute_rouge(predictions: List[str], references: List[str]) -> Dict[str, float]:
    """
    Calcule les scores ROUGE-1, ROUGE-2 et ROUGE-L.

    Args:
        predictions: Liste de textes générés.
        references: Liste de textes de référence.

    Returns:
        Dict avec rouge1, rouge2, rougeL (F-mesure, 0-1).
    """
    try:
        from rouge_score import rouge_scorer
    except ImportError:
        raise ImportError("Installez rouge-score: pip install rouge-score")

    scorer = rouge_scorer.RougeScorer(
        ["rouge1", "rouge2", "rougeL"], use_stemmer=False
    )

    scores: Dict[str, float] = {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
    n = len(predictions)
    if n == 0:
        return scores

    for pred, ref in zip(predictions, references):
        result = scorer.score(ref, pred)
        scores["rouge1"] += result["rouge1"].fmeasure
        scores["rouge2"] += result["rouge2"].fmeasure
        scores["rougeL"] += result["rougeL"].fmeasure

    return {k: round(v / n, 4) for k, v in scores.items()}


# ---------------------------------------------------------------------------
# Perplexité
# ---------------------------------------------------------------------------

def compute_perplexity(
    model,
    tokenizer,
    texts: List[str],
    max_length: int = 512,
    device: Optional[str] = None,
) -> float:
    """
    Calcule la perplexité du modèle sur une liste de textes.

    Une perplexité plus basse = meilleure modélisation du langage.

    Args:
        model: Modèle transformers (AutoModelForCausalLM).
        tokenizer: Tokenizer correspondant.
        texts: Liste de textes à évaluer.
        max_length: Longueur maximale en tokens.
        device: Device ('cpu', 'cuda', etc.).

    Returns:
        Perplexité moyenne (float).
    """
    if device is None:
        device = str(next(model.parameters()).device)

    model.eval()
    total_loss = 0.0
    total_tokens = 0

    with torch.no_grad():
        for text in texts:
            encodings = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
            )
            input_ids = encodings["input_ids"].to(device)
            n_tokens = input_ids.shape[-1]

            if n_tokens < 2:
                continue  # texte trop court

            outputs = model(input_ids, labels=input_ids)
            loss = outputs.loss.item()
            total_loss += loss * n_tokens
            total_tokens += n_tokens

    if total_tokens == 0:
        return float("inf")

    avg_loss = total_loss / total_tokens
    return round(math.exp(avg_loss), 4)


# ---------------------------------------------------------------------------
# Évaluation complète
# ---------------------------------------------------------------------------

def evaluate_model(
    model,
    tokenizer,
    eval_dataset,
    instruction_key: str = "instruction",
    output_key: str = "output",
    max_new_tokens: int = 256,
    device: Optional[str] = None,
    lang: str = "ht",
) -> Dict[str, float]:
    """
    Évalue le modèle sur un dataset en calculant BLEU, ROUGE et perplexité.

    Args:
        model: Modèle fine-tuné.
        tokenizer: Tokenizer.
        eval_dataset: Dataset HuggingFace avec colonnes instruction/output.
        instruction_key: Clé de la colonne instruction.
        output_key: Clé de la colonne sortie de référence.
        max_new_tokens: Tokens max à générer par exemple.
        device: Device cible.
        lang: Langue principale pour le system prompt.

    Returns:
        Dict avec toutes les métriques.
    """
    from ayiti_ai.inference.chat import AyitiChat

    if device is None:
        device = str(next(model.parameters()).device)

    logger.info(f"Évaluation sur {len(eval_dataset)} exemples...")

    predictions = []
    references = []
    texts_for_ppl = []

    model.eval()
    chat = AyitiChat.__new__(AyitiChat)
    chat.model = model
    chat.tokenizer = tokenizer
    chat.device = device

    for item in eval_dataset:
        instruction = item.get(instruction_key, "")
        reference = item.get(output_key, "")
        if not instruction or not reference:
            continue

        pred = chat.generate(
            instruction,
            lang=lang,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )
        predictions.append(pred)
        references.append(reference)
        texts_for_ppl.append(reference)

    if not predictions:
        logger.warning("Aucun exemple évalué.")
        return {}

    metrics: Dict[str, float] = {}
    metrics.update(compute_bleu(predictions, references))
    metrics.update(compute_rouge(predictions, references))
    metrics["perplexity"] = compute_perplexity(model, tokenizer, texts_for_ppl, device=device)
    metrics["n_examples"] = float(len(predictions))

    logger.info("Résultats d'évaluation:")
    for k, v in metrics.items():
        logger.info(f"  {k}: {v}")

    return metrics


def main() -> None:
    """Point d'entrée CLI pour l'évaluation (placeholder)."""
    print("ayiti-eval: lance scripts/run_evaluation.py pour une évaluation complète.")
