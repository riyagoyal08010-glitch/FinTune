import json
from pathlib import Path

import torch
import yaml
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_FILE = BASE_DIR / "configs" / "sft_lora.yaml"


# ============================================================
# Load configuration
# ============================================================

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


MODEL_PATH = str(BASE_DIR / config["model_name_or_path"])
TRAIN_FILE = BASE_DIR / config["train_file"]
EVAL_FILE = BASE_DIR / config["eval_file"]
OUTPUT_DIR = BASE_DIR / config["output_dir"]


# ============================================================
# Environment
# ============================================================

CUDA_AVAILABLE = torch.cuda.is_available()

print("=" * 60)
print("FinTune SFT Pipeline")
print("=" * 60)

print(f"CUDA available: {CUDA_AVAILABLE}")

if CUDA_AVAILABLE:
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        f"VRAM: "
        f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
    )
else:
    print("Running in CPU mode")
    print("Model loading will be skipped in local validation mode.")


# ============================================================
# Load datasets
# ============================================================

def load_json_dataset(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return Dataset.from_list(data)


train_dataset = load_json_dataset(TRAIN_FILE)
eval_dataset = load_json_dataset(EVAL_FILE)

print("\nDataset")
print(f"Train examples: {len(train_dataset)}")
print(f"Eval examples:  {len(eval_dataset)}")

if not CUDA_AVAILABLE:
    print("\n" + "=" * 60)
    print("LOCAL VALIDATION MODE")
    print("=" * 60)

    print("Dataset loading: OK")
    print("3B model/tokenizer loading skipped.")
    print("Run the actual training pipeline on a CUDA GPU.")

    raise SystemExit(0)


# ============================================================
# Tokenizer
# ============================================================

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    use_fast=True,
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("\nTokenizer")
print(f"EOS token: {repr(tokenizer.eos_token)}")
print(f"PAD token: {repr(tokenizer.pad_token)}")


# ============================================================
# Chat formatting
# ============================================================

FINETUNE_DATE = "01 Jan 2026"


def formatting_func(example):
    return tokenizer.apply_chat_template(
        example["messages"],
        tokenize=False,
        add_generation_prompt=False,
        date_string=FINETUNE_DATE,
    )

# Test formatting on one example
formatted_example = formatting_func(train_dataset[0])

print("\nChat template test")
print("-" * 60)
print(formatted_example[:500])
print("-" * 60)


# ============================================================
# LoRA configuration
# ============================================================

peft_config = LoraConfig(
    r=config["lora_r"],
    lora_alpha=config["lora_alpha"],
    lora_dropout=config["lora_dropout"],
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    ],
)

print("\nLoRA configuration")
print(f"Rank: {config['lora_r']}")
print(f"Alpha: {config['lora_alpha']}")
print(f"Dropout: {config['lora_dropout']}")
print("Target modules: q_proj, k_proj, v_proj, o_proj")

# ============================================================
# Model loading
# ============================================================

print("\nLoading model...")

if torch.cuda.is_bf16_supported():
    model_dtype = torch.bfloat16
else:
    model_dtype = torch.float16

print(f"Model dtype: {model_dtype}")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=model_dtype,
)

model.config.pad_token_id = tokenizer.pad_token_id

print("Model loaded successfully.")


# ============================================================
# SFT configuration
# ============================================================

training_args = SFTConfig(
    output_dir=str(OUTPUT_DIR),

    num_train_epochs=config["num_train_epochs"],
    learning_rate=config["learning_rate"],

    per_device_train_batch_size=config["per_device_train_batch_size"],
    per_device_eval_batch_size=config["per_device_eval_batch_size"],
    gradient_accumulation_steps=config["gradient_accumulation_steps"],

    gradient_checkpointing=config["gradient_checkpointing"],
    warmup_ratio=config["warmup_ratio"],

    logging_steps=config["logging_steps"],

    eval_strategy=config["eval_strategy"],
    eval_steps=config["eval_steps"],

    save_strategy=config["save_strategy"],
    save_steps=config["save_steps"],
    save_total_limit=config["save_total_limit"],

    max_length=config["max_seq_length"],
    packing=False,

    completion_only_loss=True,

    seed=config["seed"],

    report_to="none",
)


# ============================================================
# Trainer
# ============================================================

trainer = SFTTrainer(
    model=model,
    args=training_args,

    train_dataset=train_dataset,
    eval_dataset=eval_dataset,

    processing_class=tokenizer,

    formatting_func=formatting_func,

    peft_config=peft_config,
)


# ============================================================
# Ready
# ============================================================

print("\n" + "=" * 60)
print("SFT TRAINER CREATED SUCCESSFULLY")
print("=" * 60)

print(f"Train examples: {len(train_dataset)}")
print(f"Eval examples:  {len(eval_dataset)}")
print(f"Max sequence length: {config['max_seq_length']}")

print("\nTraining has NOT started.")