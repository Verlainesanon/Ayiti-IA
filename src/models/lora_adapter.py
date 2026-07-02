from peft import LoraConfig, get_peft_model
import yaml


def get_lora_config(
    r: int = 16,
    alpha: int = 32,
    dropout: float = 0.05,
    target_modules: list = None,
    task_type: str = "CAUSAL_LM",
) -> LoraConfig:
    """
    Crée et retourne un objet LoraConfig PEFT.

    Args:
        r: Rang de la décomposition LoRA.
        alpha: Facteur de scaling LoRA (lora_alpha).
        dropout: Taux de dropout LoRA.
        target_modules: Liste des modules à adapter (défaut : q/k/v/o_proj).
        task_type: Type de tâche PEFT (CAUSAL_LM pour generation).

    Returns:
        LoraConfig configuré.
    """
    if target_modules is None:
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]

    return LoraConfig(
        r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        target_modules=target_modules,
        bias="none",
        task_type=task_type,
    )


def apply_lora(model, config_path: str = "config/lora_config.yaml"):
    """
    Applique un adaptateur LoRA à un modèle depuis un fichier YAML.

    Args:
        model: Le modèle de base (transformers).
        config_path: Chemin vers le fichier YAML de configuration LoRA.

    Returns:
        Modèle avec adaptateur LoRA attaché.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        lora_config_dict = yaml.safe_load(f)

    lora_config = LoraConfig(**lora_config_dict)
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model
