# Local LLM Deployment Guide

Complete guide for deploying the fine-tuned local LLM model.

## Quick Start

### Option 1: RunPod (Recommended - Easiest)

**Cost:** ~$0.40/hour ($150/month for 24/7)

1. **Sign up at runpod.io**
   ```
   https://www.runpod.io/
   ```

2. **Deploy template**
   - Click "Deploy"  - Select "RTX 4090" or "A100 40GB"
   - Choose "PyTorch" template
   - Add your GitHub repo
   - Set startup command:
     ```bash
     cd /workspace/Suno_Personas/local_llm &&
     pip install -r requirements.txt &&
     python inference/inference_server.py --model-path /workspace/model --port 8001
     ```

3. **Upload model**
   ```bash
   runpod upload ./training/checkpoints/merged /workspace/model
   ```

4. **Get endpoint URL**
   - RunPod will provide: `https://your-pod-id.runpod.net:8001`
   - Add to backend `.env`: `LOCAL_LLM_URL=https://your-pod-id.runpod.net:8001`

### Option 2: Modal (Serverless - Best for Variable Traffic)

**Cost:** Pay only for usage (~$0.0001/second compute)

1. **Install Modal**
   ```bash
   pip install modal
   modal setup
   ```

2. **Deploy**
   ```bash
   cd local_llm/inference
   modal deploy modal_deploy.py
   ```

3. **Get endpoint**
   ```bash
   modal app show song-score-llm
   ```

### Option 3: Self-Hosted (Best for High Volume)

**Cost:** ~$100-200/month (Hetzner GPU server)

1. **Rent GPU server**
   - Hetzner: https://www.hetzner.com/
   - Pick server with RTX 4090 or A100

2. **SSH and setup**
   ```bash
   ssh root@your-server-ip

   # Install CUDA
   wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
   sudo dpkg -i cuda-keyring_1.0-1_all.deb
   sudo apt-get update
   sudo apt-get -y install cuda

   # Clone repo
   git clone https://github.com/youruser/Suno_Personas.git
   cd Suno_Personas/local_llm

   # Install dependencies
   pip install -r requirements.txt

   # Download trained model (from your training run)
   # Option A: Copy from local
   scp -r ./training/checkpoints/merged root@server:/workspace/model

   # Option B: Download from Hugging Face (if uploaded)
   # huggingface-cli download youruser/song-score-llm

   # Start inference server with systemd
   sudo nano /etc/systemd/system/song-score-llm.service
   ```

3. **Create systemd service**
   ```ini
   [Unit]
   Description=Song Score LLM Inference Server
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/Suno_Personas/local_llm
   ExecStart=/usr/bin/python3 inference/inference_server.py --model-path /workspace/model --port 8001
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable song-score-llm
   sudo systemctl start song-score-llm
   sudo systemctl status song-score-llm
   ```

5. **Configure firewall**
   ```bash
   sudo ufw allow 8001/tcp
   ```

---

## Integration with Backend

Once your model is deployed, update the backend configuration:

### 1. Update `.env`

```bash
cd backend
nano .env
```

Add/update:
```
# Enable hybrid mode (local + cloud fallback)
LLM_PROVIDER=hybrid
ENABLE_HYBRID_MODE=true
USE_LOCAL_LLM=true
LOCAL_LLM_URL=http://your-server:8001  # or https://your-pod.runpod.net:8001

# Keep cloud API keys for fallback
OPENAI_API_KEY=your-key
CRITICAL_PERSONAS_CLOUD=true

# Optional: Enable caching for even more savings
ENABLE_CACHING=true
REDIS_URL=redis://localhost:6379
```

### 2. Start Redis (if caching enabled)

```bash
docker run -d -p 6379:6379 redis:alpine
```

### 3. Restart backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 4. Test integration

```bash
curl http://localhost:8000/health
# Should show: "llm_provider": "hybrid"
```

---

## Monitoring & Optimization

### Performance Monitoring

Check inference server metrics:
```bash
curl http://your-server:8001/metrics
```

Expected performance:
- Latency: 2-4s per persona
- Throughput: 50-100 tokens/second
- Concurrent: 10 personas in ~10s

### Cost Tracking

**Before (Cloud Only):**
- 1,000 analyses/day = $30/day = $900/month

**After (Hybrid + Local):**
- GPU server: $150/month
- Fallback API calls: ~$30/month (10% of requests)
- Redis caching: $25/month
- **Total: ~$205/month**

**Savings: $695/month (77% reduction)**

### Optimization Tips

1. **Batch Processing**
   ```python
   # Group requests to leverage batch inference
   results = await local_client.evaluate_batch(personas, track)
   ```

2. **Caching Strategy**
   ```python
   # Cache common track patterns
   # Similar genres/moods get similar evaluations
   ```

3. **GPU Utilization**
   ```bash
   # Monitor GPU usage
   nvidia-smi

   # If underutilized, increase batch size
   # If OOM, reduce batch size or use 4-bit quantization
   ```

4. **Load Balancing**
   ```bash
   # For high traffic, run multiple inference servers
   # Use nginx load balancer
   ```

---

## Troubleshooting

### Model Not Loading

**Error:** "Out of memory"
```bash
# Use 4-bit quantization
python inference/inference_server.py \
  --model-path /workspace/model \
  --load-in-4bit
```

### Slow Inference

**Problem:** >5s per persona

**Solutions:**
```bash
# 1. Use FP16 instead of FP32
--dtype half

# 2. Increase tensor parallelism (multi-GPU)
--tensor-parallel-size 2

# 3. Reduce max sequence length
--max-model-len 512

# 4. Use flash attention
--use-flash-attention
```

### Quality Issues

**Problem:** Local model responses are poor

**Solutions:**
1. Check if model was trained properly:
   ```bash
   python ../scripts/evaluate_model.py
   ```

2. Increase temperature for more diversity:
   ```python
   sampling_params = SamplingParams(temperature=0.8)
   ```

3. Fallback to cloud for critical personas:
   ```bash
   CRITICAL_PERSONAS_CLOUD=true
   ```

4. Retrain with more data:
   ```bash
   python ../data_generation/generate_synthetic_data.py --num-examples 10000
   ```

### Connection Issues

**Error:** "Connection refused"

**Check:**
```bash
# 1. Is server running?
systemctl status song-score-llm

# 2. Is port open?
sudo ufw status
sudo ufw allow 8001/tcp

# 3. Is firewall blocking?
telnet your-server 8001

# 4. Check logs
journalctl -u song-score-llm -f
```

---

## Scaling

### Horizontal Scaling (Multiple Servers)

For >10,000 analyses/day:

1. **Deploy multiple inference servers**
   ```bash
   # Server 1
   python inference_server.py --port 8001

   # Server 2
   python inference_server.py --port 8002

   # Server 3
   python inference_server.py --port 8003
   ```

2. **Add load balancer (nginx)**
   ```nginx
   upstream llm_backend {
       server localhost:8001;
       server localhost:8002;
       server localhost:8003;
   }

   server {
       listen 8000;
       location / {
           proxy_pass http://llm_backend;
       }
   }
   ```

3. **Update backend config**
   ```
   LOCAL_LLM_URL=http://load-balancer:8000
   ```

### Vertical Scaling (Bigger GPU)

| GPU | VRAM | Cost/hr | Throughput |
|-----|------|---------|------------|
| RTX 4090 | 24GB | $0.40 | 100 tok/s |
| A100 40GB | 40GB | $1.10 | 150 tok/s |
| A100 80GB | 80GB | $1.80 | 200 tok/s |

---

## Backup & Disaster Recovery

### Model Backups

```bash
# Upload trained model to Hugging Face
huggingface-cli upload youruser/song-score-llm ./training/checkpoints/merged

# Or use cloud storage
aws s3 sync ./training/checkpoints/merged s3://your-bucket/models/
```

### Graceful Fallback

Backend automatically falls back to cloud if local fails:

```python
# In hybrid_persona_engine.py
try:
    result = await local_client.evaluate(persona, track)
except:
    result = await cloud_engine.evaluate(persona, track)
```

### Health Checks

```bash
# Monitor endpoint
while true; do
  curl -f http://your-server:8001/health || echo "ALERT: Server down!"
  sleep 60
done
```

---

## Cost Calculator

Use this to estimate your costs:

**Input:**
- Analyses per day: ___
- Average personas per analysis: ___

**Cloud Cost (GPT-4):**
- Cost = analyses × personas × $0.003
- Example: 1,000 × 10 × $0.003 = $30/day = $900/month

**Local Cost:**
- GPU rental: $150/month
- Fallback API (10%): $90/month
- Redis: $25/month
- **Total: $265/month**

**Breakeven:**
- Cloud = Local when: analyses/day × 30 × 0.003 × 10 = $150
- **Breakeven: ~167 analyses/day**

If you're doing more than 167 analyses/day, local LLM is cheaper!

---

## Next Steps

1. ✅ Deploy inference server
2. ✅ Integrate with backend
3. ✅ Enable caching
4. ✅ Monitor performance
5. ✅ Track cost savings
6. 🔄 Continuously retrain with new data

See [LOCAL_LLM_PLAN.md](../LOCAL_LLM_PLAN.md) for the complete strategy.
