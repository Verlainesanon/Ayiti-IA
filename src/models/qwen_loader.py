from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch


def load_qwen_model_and_tokenizer(
    model_name: str = "Qwen/Qwen2.5-7B-Instruct",
    use_quantization: bool = True,
):
    """
    Charge le modèle Qwen2.5 et son tokenizer.

    Args:
        model_name: Identifiant HuggingFace du modèle (ex: Qwen/Qwen2.5-7B-Instruct).
        use_quantization: Si True, charge en 4-bit NF4 (pour GPU limités / Colab).
                          Si False, charge en float16 sur CPU (pour test local).

    Returns:
        (model, tokenizer)
    """
    if use_quantization:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="cpu",
            trust_remote_code=True,
        )

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer


# Alias rétrocompatible
def load_qwen_model(model_name: str = "Qwen/Qwen2.5-7B-Instruct", quantize: bool = True):
    """Alias pour load_qwen_model_and_tokenizer (compatibilité ascendante)."""
    return load_qwen_model_and_tokenizer(model_name, use_quantization=quantize)
