# LoRA Adapters

This directory stores LoRA adapters for the experiment.

## Getting Adapters

Run the setup script to download sample adapters:

```bash
python setup_adapters.py
```

Or manually download from HuggingFace:

```bash
# Using huggingface-cli
huggingface-cli download lewtun/Qwen2.5-0.5B-SFT-LoRA --local-dir ./adapters/sft-lora

# Or using git
git lfs install
git clone https://huggingface.co/lewtun/Qwen2.5-0.5B-SFT-LoRA ./adapters/sft-lora
```

## Directory Structure

After downloading, this directory should contain:

```
adapters/
├── README.md
├── sft-lora/
│   ├── adapter_config.json
│   ├── adapter_model.safetensors
│   └── ...
└── other-adapter/
    └── ...
```

## Creating Your Own Adapters

Use PEFT or TRL to fine-tune:

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,  # rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
)

model = get_peft_model(base_model, config)
# Train...
model.save_pretrained("./adapters/my-adapter")
```
