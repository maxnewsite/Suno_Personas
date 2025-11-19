"""
Fine-tune Llama 3.1 8B for persona-based music evaluation.

Uses QLoRA for efficient 4-bit training on a single GPU.
"""

import os
import torch
import argparse
from pathlib import Path
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
import wandb


def format_instruction(example):
    """Format example for instruction tuning."""
    return {
        "text": f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a music evaluation persona. Analyze tracks and respond with JSON only.<|eot_id|><|start_header_id|>user<|end_header_id|>

{example['instruction']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{example['output']}<|eot_id|>"""
    }


def load_model_and_tokenizer(model_name: str, use_4bit: bool = True):
    """Load model with quantization config."""

    if use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
    else:
        bnb_config = None

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True
    )
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )

    # Prepare for k-bit training
    model = prepare_model_for_kbit_training(model)

    return model, tokenizer


def get_lora_config():
    """Configure LoRA parameters."""
    return LoraConfig(
        r=16,  # Rank
        lora_alpha=32,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )


def main():
    parser = argparse.ArgumentParser(description="Fine-tune Llama 3.1 for persona evaluation")
    parser.add_argument(
        "--model-name",
        type=str,
        default="meta-llama/Llama-3.1-8B-Instruct",
        help="Base model name"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="../data",
        help="Directory containing train.jsonl and val.jsonl"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./checkpoints",
        help="Output directory for model checkpoints"
    )
    parser.add_argument(
        "--num-epochs",
        type=int,
        default=3,
        help="Number of training epochs"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Training batch size per device"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=2e-4,
        help="Learning rate"
    )
    parser.add_argument(
        "--max-seq-length",
        type=int,
        default=1024,
        help="Maximum sequence length"
    )
    parser.add_argument(
        "--use-wandb",
        action="store_true",
        help="Use Weights & Biases for logging"
    )

    args = parser.parse_args()

    # Initialize wandb if requested
    if args.use_wandb:
        wandb.init(
            project="song-score-llm",
            config=vars(args)
        )

    print("🚀 Starting fine-tuning process...")
    print(f"Model: {args.model_name}")
    print(f"Data: {args.data_dir}")
    print(f"Output: {args.output_dir}\n")

    # Load datasets
    print("📚 Loading datasets...")
    data_files = {
        "train": f"{args.data_dir}/train.jsonl",
        "validation": f"{args.data_dir}/val.jsonl"
    }
    dataset = load_dataset("json", data_files=data_files)

    # Format datasets
    print("📝 Formatting datasets...")
    train_dataset = dataset["train"].map(format_instruction)
    val_dataset = dataset["validation"].map(format_instruction)

    print(f"Train examples: {len(train_dataset)}")
    print(f"Val examples: {len(val_dataset)}\n")

    # Load model and tokenizer
    print("🔧 Loading model and tokenizer...")
    model, tokenizer = load_model_and_tokenizer(args.model_name)

    # Configure LoRA
    print("⚙️  Configuring LoRA...")
    lora_config = get_lora_config()
    model = get_peft_model(model, lora_config)

    # Print trainable parameters
    model.print_trainable_parameters()

    # Training arguments
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=4,
        gradient_checkpointing=True,
        optim="paged_adamw_32bit",
        learning_rate=args.learning_rate,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="epoch",
        do_eval=True,
        bf16=True,  # Use bfloat16
        tf32=True,
        max_grad_norm=0.3,
        warmup_steps=100,
        group_by_length=True,
        report_to="wandb" if args.use_wandb else "none",
    )

    # Initialize trainer
    print("👨‍🏫 Initializing trainer...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        peft_config=lora_config,
        max_seq_length=args.max_seq_length,
        tokenizer=tokenizer,
        args=training_args,
        dataset_text_field="text",
    )

    # Train
    print("\n🏋️  Starting training...\n")
    trainer.train()

    # Save final model
    print("\n💾 Saving final model...")
    trainer.save_model(f"{args.output_dir}/final")

    # Save merged model (base + LoRA)
    print("🔗 Merging LoRA weights with base model...")
    model = model.merge_and_unload()
    model.save_pretrained(f"{args.output_dir}/merged")
    tokenizer.save_pretrained(f"{args.output_dir}/merged")

    print("\n✅ Training complete!")
    print(f"Model saved to: {args.output_dir}/merged")
    print("\n🎯 Next steps:")
    print("1. Evaluate the model: python ../scripts/evaluate_model.py")
    print("2. Deploy inference: python ../inference/inference_server.py")


if __name__ == "__main__":
    main()
