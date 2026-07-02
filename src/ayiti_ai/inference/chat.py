"""
Module d'inférence pour Ayiti-AI.

Permet de dialoguer avec le modèle Qwen fine-tuné en créole haïtien,
français ou anglais via une interface de chat simple.
"""

import logging
from collections.abc import Iterator
from typing import Any

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)


class AyitiChat:
    """
    Interface de chat multilingue pour Ayiti-AI.

    Supports: ht (Kreyòl ayisyen), fr (Français), en (English).

    Exemple d'utilisation:
        chat = AyitiChat(base_model="Qwen/Qwen2.5-1.5B-Instruct")
        response = chat.generate("Bonjou! Kijan ou rele?", lang="ht")
        print(response)
    """

    SYSTEM_PROMPTS: dict[str, str] = {
        "ht": (
            "Ou se Ayiti-AI, yon asistan entèlijan ki pale kreyòl ayisyen, "
            "fransè ak anglè. Ou konprann kilti ak kontèks ayisyen. "
            "Reponn ak rispè, klète ak konpasyon."
        ),
        "fr": (
            "Tu es Ayiti-AI, un assistant intelligent qui parle créole haïtien, "
            "français et anglais. Tu comprends la culture et le contexte haïtien. "
            "Réponds avec respect, clarté et bienveillance."
        ),
        "en": (
            "You are Ayiti-AI, an intelligent assistant fluent in Haitian Creole, "
            "French, and English. You understand Haitian culture and context. "
            "Respond with respect, clarity, and compassion."
        ),
    }

    def __init__(
        self,
        base_model: str = "Qwen/Qwen2.5-1.5B-Instruct",
        adapter_path: str | None = None,
        device: str | None = None,
    ):
        """
        Initialise le modèle et le tokenizer.

        Args:
            base_model: Identifiant HuggingFace du modèle de base.
            adapter_path: Chemin vers un adaptateur LoRA (optionnel).
            device: Forcer un device ('cpu', 'cuda', 'mps'). Auto-détecté si None.
        """
        self.device = device or self._detect_device()
        logger.info(f"Device: {self.device}")

        logger.info(f"Chargement du tokenizer: {base_model}")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        logger.info(f"Chargement du modèle: {base_model}")
        self.model: Any = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
            device_map=self.device,
            trust_remote_code=True,
        )

        if adapter_path:
            logger.info(f"Chargement de l'adaptateur LoRA: {adapter_path}")
            self.model = PeftModel.from_pretrained(self.model, adapter_path)
            self.model = self.model.merge_and_unload()

        self.model.eval()

    def _detect_device(self) -> str:
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _build_messages(
        self,
        user_input: str,
        lang: str = "ht",
        history: list[dict] | None = None,
    ) -> list[dict]:
        """Construit la liste de messages au format ChatML."""
        lang = lang if lang in self.SYSTEM_PROMPTS else "ht"
        messages: list[dict] = [{"role": "system", "content": self.SYSTEM_PROMPTS[lang]}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_input})
        return messages

    def generate(
        self,
        user_input: str,
        lang: str = "ht",
        history: list[dict] | None = None,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        do_sample: bool = True,
    ) -> str:
        """
        Génère une réponse à partir d'une entrée utilisateur.

        Args:
            user_input: Message de l'utilisateur.
            lang: Langue principale ('ht', 'fr', 'en').
            history: Historique de conversation (liste de dicts role/content).
            max_new_tokens: Nombre maximal de tokens à générer.
            temperature: Température d'échantillonnage.
            top_p: Nucleus sampling top-p.
            do_sample: Utiliser l'échantillonnage (False = greedy).

        Returns:
            Réponse générée sous forme de chaîne.
        """
        messages = self._build_messages(user_input, lang, history)

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Décoder seulement les nouveaux tokens
        new_tokens = outputs[0][inputs["input_ids"].shape[-1] :]
        response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        if isinstance(response, list):
            response = " ".join(response)
        return response.strip()

    def generate_stream(
        self,
        user_input: str,
        lang: str = "ht",
        max_new_tokens: int = 512,
    ) -> Iterator[str]:
        """Génère une réponse token par token (streaming)."""
        # TODO: implémenter avec TextIteratorStreamer
        raise NotImplementedError("Le streaming sera implémenté avec TextIteratorStreamer.")

    def chat_loop(self, lang: str = "ht") -> None:
        """Lance une boucle de conversation interactive en terminal."""
        lang_names = {"ht": "Kreyòl", "fr": "Français", "en": "English"}
        print(f"\n🇭🇹 Ayiti-AI — {lang_names.get(lang, lang)}")
        print("Tape 'quit' pou sòti / Tapez 'quit' pour quitter\n")

        history: list[dict] = []
        while True:
            try:
                user_input = input("Ou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nAurevwa! / Goodbye!")
                break

            if user_input.lower() in ("quit", "exit", "sòti"):
                print("Aurevwa! 🇭🇹")
                break
            if not user_input:
                continue

            response = self.generate(user_input, lang=lang, history=history)
            print(f"Ayiti-AI: {response}\n")

            history.extend(
                [
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": response},
                ]
            )


def main() -> None:
    """Point d'entrée CLI pour l'interface de chat."""
    import argparse

    parser = argparse.ArgumentParser(description="Ayiti-AI Chat Interface")
    parser.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    parser.add_argument("--adapter", default=None, help="Chemin vers le LoRA adapter")
    parser.add_argument("--lang", default="ht", choices=["ht", "fr", "en"])
    args = parser.parse_args()

    chat = AyitiChat(base_model=args.model, adapter_path=args.adapter)
    chat.chat_loop(lang=args.lang)


if __name__ == "__main__":
    main()
