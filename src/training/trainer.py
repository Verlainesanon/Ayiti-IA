import os
import torch
from transformers import AutoTokenizer, TrainingArguments
from trl import SFTTrainer
from peft import LoraConfig, get_peft_model
from src.models.qwen_loader import load_qwen_model_and_tokenizer
from src.models.lora_adapter import get_lora_config

def train_sft(
    model_name_or_path: str,
    train_file_path: str,
    val_file_path: str = None,
    output_dir: str = "./results",
    epochs: int = 3,
    batch_size: int = 1,
    gradient_accumulation_steps: int = 4,
    learning_rate: float = 2e-4,
    lora_r: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.05,
    max_seq_length: int = 1024
):
    print("Loading model and tokenizer...")
    has_cuda = torch.cuda.is_available()
    use_quantization = has_cuda
    print(f"Quantization: {use_quantization} (CUDA is_available: {has_cuda})")
    model, tokenizer = load_qwen_model_and_tokenizer(model_name_or_path, use_quantization=use_quantization)
    
    # Load dataset
    from datasets import load_dataset
    print("Loading dataset...")
    data_files = {"train": train_file_path}
    if val_file_path:
        data_files["validation"] = val_file_path
    
    dataset = load_dataset("json", data_files=data_files)
    
    # LoRA config
    peft_config = get_lora_config(r=lora_r, alpha=lora_alpha, dropout=lora_dropout)
    
    fp16_val = False
    bf16_val = False
    if has_cuda:
        if torch.cuda.is_bf16_supported():
            bf16_val = True
        else:
            fp16_val = True

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        learning_rate=learning_rate,
        fp16=fp16_val,
        bf16=bf16_val,
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="epoch" if val_file_path else "no",
        save_total_limit=2,
        report_to="none",
        optim="adamw_torch" if has_cuda else "adamw_hf"
    )
    
    # Formatting function for dataset (Qwen chat ML format)
    def formatting_prompts_func(example):
        output_texts = []
        if 'messages' in example:
            messages_list = example['messages']
            # Handle both batched (list of lists) and single example
            if not isinstance(messages_list, list) or (messages_list and not isinstance(messages_list[0], list)):
                messages_list = [messages_list]
            for messages in messages_list:
                text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
                output_texts.append(text)
        else:
            instructions = example.get('instruction', [])
            outputs = example.get('output', [])
            inputs = example.get('input', None)

            if not isinstance(instructions, list):
                instructions = [instructions]
                outputs = [outputs]
                inputs = [inputs] if inputs is not None else [None]
            elif inputs is None:
                inputs = [None] * len(instructions)

            for inst, out, inp in zip(instructions, outputs, inputs):
                user_content = f"{inst}\n{inp}".strip() if inp else inst
                messages = [
                    {
                        "role": "system",
                        "content": "Ou se Ayiti-AI, yon asistan entèlijan ki pale kreyòl ayisyen, fransè ak anglè. Ou konprann kilti ak kontèks ayisyen. Reponn ak rispè, klète ak konpasyon."
                    },
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": out}
                ]
                text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
                output_texts.append(text)
        return output_texts

    print("Initializing trainer...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"] if val_file_path else None,
        peft_config=peft_config,
        max_seq_length=max_seq_length,
        formatting_func=formatting_prompts_func,
        tokenizer=tokenizer,
        args=training_args,
    )
    
    print("Starting training...")
    trainer.train()
    
    print(f"Saving PEFT adapter to {output_dir}...")
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Training completed successfully.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name_or_path", type=str, default="Qwen/Qwen2.5-1.5B-Instruct")
    parser.add_argument("--train_file", type=str, required=True)
    parser.add_argument("--val_file", type=str, default=None)
    parser.add_argument("--output_dir", type=str, default="./results")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=1)
    args = parser.parse_args()
    
    train_sft(
        model_name_or_path=args.model_name_or_path,
        train_file_path=args.train_file,
        val_file_path=args.val_file,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size
    )
