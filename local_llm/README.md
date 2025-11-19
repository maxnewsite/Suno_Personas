# Local LLM Training & Inference

Infrastructure for fine-tuning and deploying a local LLM model to reduce API costs by 70-90%.

## Overview

This system replaces expensive cloud API calls (GPT-4/Claude) with a fine-tuned Llama 3.1 8B model for persona-based music analysis.

**Cost Savings:**
- Current: $900/month (1,000 analyses/day)
- With local model: $200/month
- **Savings: $700/month (78% reduction)**

## Components

### 1. Data Generation (`data_generation/`)
Generate synthetic training data using GPT-4 for fine-tuning.

**Goal:** 5,000 diverse track profiles with 10 persona responses each = 50,000 training examples

**Cost:** ~$300 one-time

### 2. Training (`training/`)
Fine-tune Llama 3.1 8B using QLoRA for efficient training.

**Requirements:**
- GPU: NVIDIA A100 40GB or RTX 4090 24GB
- Time: 2-4 hours
- Cost: ~$50 on RunPod/Vast.ai

### 3. Inference (`inference/`)
Deploy fine-tuned model for fast inference using vLLM.

**Performance:**
- Latency: 2-4 seconds per persona
- Throughput: 50-100 tokens/second
- Cost: $150/month (24/7 GPU)

### 4. Evaluation (`scripts/`)
Compare local model quality against GPT-4 baseline.

## Quick Start

### Step 1: Generate Training Data

```bash
cd data_generation
python generate_synthetic_data.py --num-examples 5000 --output-dir ../data
```

This creates:
- `train.jsonl` (4,000 examples)
- `val.jsonl` (500 examples)
- `test.jsonl` (500 examples)

### Step 2: Fine-Tune Model

```bash
cd training
python train_persona_model.py \
  --model-name meta-llama/Llama-3.1-8B-Instruct \
  --data-dir ../data \
  --output-dir ./checkpoints \
  --num-epochs 3 \
  --batch-size 4
```

Trains for ~2-4 hours on A100.

### Step 3: Deploy Inference Server

```bash
cd inference
python inference_server.py \
  --model-path ../training/checkpoints/best \
  --port 8001
```

### Step 4: Integrate with Backend

Update `backend/app/config.py`:
```python
LLM_PROVIDER = "hybrid"  # Use local + cloud fallback
LOCAL_LLM_URL = "http://localhost:8001"
```

## Directory Structure

```
local_llm/
├── data_generation/
│   ├── generate_synthetic_data.py    # Generate training data
│   ├── data_validator.py             # Validate data quality
│   └── persona_templates.py          # Persona prompt templates
├── training/
│   ├── train_persona_model.py        # Main training script
│   ├── config.yaml                   # Training configuration
│   └── trainer_utils.py              # Helper functions
├── inference/
│   ├── inference_server.py           # vLLM inference server
│   ├── model_wrapper.py              # Model interface
│   └── batch_processor.py            # Batch inference
├── scripts/
│   ├── evaluate_model.py             # Quality evaluation
│   ├── benchmark.py                  # Performance testing
│   └── compare_with_gpt4.py          # A/B comparison
└── data/                              # Generated datasets
    ├── train.jsonl
    ├── val.jsonl
    └── test.jsonl
```

## Deployment Options

### Option A: RunPod (Recommended)
```bash
# Cheap GPU rental ($0.30-0.50/hour)
runpod deploy --gpu "RTX 4090" --script inference/inference_server.py
```

### Option B: Modal
```bash
# Serverless GPU inference
modal deploy inference/modal_deploy.py
```

### Option C: Self-Hosted
```bash
# On your own GPU server (Hetzner, etc.)
docker build -t song-score-llm .
docker run -p 8001:8001 --gpus all song-score-llm
```

## Cost Breakdown

### One-Time Costs
- Data generation (GPT-4): $300
- Training (GPU rental): $50
- **Total: $350**

### Monthly Costs
- GPU server (24/7): $150
- Monitoring: $20
- Fallback API calls: $30
- **Total: $200/month**

### Comparison
- **Before:** $900/month
- **After:** $200/month
- **ROI:** Breakeven in <1 month

## Performance Targets

### Quality (vs GPT-4 baseline)
- Response similarity: >90%
- JSON format validity: >99%
- Persona consistency: >95%
- User satisfaction: >4/5

### Speed
- Per-persona latency: <3s
- Full analysis (10 personas): <15s
- Throughput: >100 analyses/hour

### Cost
- Cost per analysis: <$0.005
- Total monthly: <$250
- Savings vs cloud: >70%

## Monitoring

Track these metrics:
- Model inference latency
- Response quality scores
- Fallback rate to cloud API
- Cost per analysis
- Error rate

Dashboard available at: `http://localhost:8001/metrics`

## Troubleshooting

### Out of Memory (OOM)
```bash
# Reduce batch size
--batch-size 2

# Use 4-bit quantization
--load-in-4bit
```

### Slow Inference
```bash
# Increase parallelism
--tensor-parallel-size 2

# Use FP16
--dtype half
```

### Quality Issues
```bash
# Retrain with more data
python generate_synthetic_data.py --num-examples 10000

# Adjust training params
--learning-rate 1e-4 --num-epochs 5
```

## Next Steps

1. ✅ Generate training data
2. ✅ Fine-tune model
3. ✅ Deploy inference server
4. ✅ Integrate with backend
5. ✅ A/B test quality
6. ✅ Monitor and iterate

See [LOCAL_LLM_PLAN.md](../LOCAL_LLM_PLAN.md) for complete strategy.
