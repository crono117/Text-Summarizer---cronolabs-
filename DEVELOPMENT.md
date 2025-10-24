# Development Guide - SummaSaaS

## Two Development Modes

This project supports two development modes:

### 1. **Lite Mode** (Codespaces/Low Resources)
- **Best for**: GitHub Codespaces, lightweight development, UI/API work
- **Excludes**: PyTorch, Transformers, heavy ML libraries
- **Resources**: ~4GB RAM, ~5GB disk
- **Startup**: ~2-3 minutes

### 2. **Full Mode** (Local Machine with GPU)
- **Best for**: Local development with RTX 4060, ML model testing
- **Includes**: All ML libraries (PyTorch, Transformers, etc.)
- **Resources**: 16GB+ RAM, 20GB+ disk, GPU recommended
- **Startup**: ~5-10 minutes (first build)

---

## Quick Start

### Lite Mode (Codespaces)

```bash
# Start services with lite configuration
docker-compose -f docker-compose.lite.yml up -d --build

# Run migrations
docker-compose -f docker-compose.lite.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.lite.yml exec web python manage.py createsuperuser

# Access at http://localhost:8000
```

### Full Mode (Local Machine)

```bash
# Start services with full ML capabilities
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access at http://localhost:8000
```

---

## Switching Between Modes

### From Lite to Full (When Ready to Test ML)

1. **Stop lite services:**
   ```bash
   docker-compose -f docker-compose.lite.yml down
   ```

2. **Start full services:**
   ```bash
   docker-compose up -d --build
   ```

3. **Database persists!** Your data is preserved in Docker volumes.

### From Full to Lite

1. **Stop full services:**
   ```bash
   docker-compose down
   ```

2. **Start lite services:**
   ```bash
   docker-compose -f docker-compose.lite.yml up -d --build
   ```

---

## What's Different in Lite Mode?

### Excluded Libraries:
- ❌ `torch` (PyTorch) - ~2.5GB
- ❌ `transformers` - Large NLP models
- ❌ `scikit-learn` - ML algorithms
- ❌ `sentencepiece` - Tokenizer
- ❌ `playwright` browsers - Visual testing

### Included:
- ✅ Django + REST Framework
- ✅ Celery (background tasks)
- ✅ PostgreSQL + Redis
- ✅ Stripe billing
- ✅ All API endpoints
- ✅ Authentication
- ✅ Basic testing tools

### Summarization in Lite Mode:
The app will use **simple extractive summarization** (no ML required):
- Sentence extraction based on TF-IDF
- Keyword extraction
- Text statistics

---

## Requirements Files

| File | Purpose | Size |
|------|---------|------|
| `requirements/base.txt` | Full production deps | ~8GB |
| `requirements/base-lite.txt` | Lite production deps | ~2GB |
| `requirements/dev.txt` | Full dev deps | ~10GB |
| `requirements/dev-lite.txt` | Lite dev deps | ~3GB |

---

## Docker Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Full ML capabilities |
| `docker-compose.lite.yml` | Lightweight mode |
| `Dockerfile` | Full ML image |
| `Dockerfile.lite` | Lightweight image |

---

## Environment Variables

Add to your `.env` file:

```bash
# Set to True for lite mode
USE_LITE_MODE=True

# Your app will detect this and use lightweight summarization
```

---

## Common Commands

### View Logs
```bash
# Lite mode
docker-compose -f docker-compose.lite.yml logs -f web

# Full mode
docker-compose logs -f web
```

### Restart Services
```bash
# Lite mode
docker-compose -f docker-compose.lite.yml restart

# Full mode
docker-compose restart
```

### Shell Access
```bash
# Lite mode
docker-compose -f docker-compose.lite.yml exec web bash

# Full mode
docker-compose exec web bash
```

### Run Tests
```bash
# Lite mode (no ML tests)
docker-compose -f docker-compose.lite.yml exec web pytest tests/ -v

# Full mode (all tests)
docker-compose exec web pytest tests/ -v
```

---

## Resource Usage Comparison

| Metric | Lite Mode | Full Mode |
|--------|-----------|-----------|
| **Build Time** | 2-3 min | 8-12 min |
| **Disk Space** | ~5GB | ~15GB |
| **RAM Usage** | 2-4GB | 8-16GB |
| **Docker Image** | ~1.5GB | ~6GB |
| **Python Packages** | ~50 | ~120 |

---

## Recommended Workflows

### 1. **Starting New Feature (UI/API)**
→ Use **Lite Mode** in Codespace
- Fast iteration
- No ML needed
- Quick builds

### 2. **Testing Summarization**
→ Switch to **Full Mode** locally
- Test with real models
- GPU acceleration
- Full ML pipeline

### 3. **Production Deployment**
→ Use **Full Mode**
- All features enabled
- Proper ML inference
- Production-ready

---

## Troubleshooting

### Lite Mode: "ML Library Not Found"
This is expected! In lite mode, ML features use fallback implementations.

### Full Mode: Out of Memory
- Increase Docker memory allocation (16GB recommended)
- Close other applications
- Use lighter models in settings

### Database Issues
- Volumes persist across mode switches
- To reset: `docker volume rm postgres_data`

---

## Next Steps

1. ✅ Start in **Lite Mode** for development
2. ✅ Build UI and API features
3. ✅ Switch to **Full Mode** when ready to test ML
4. ✅ Deploy with **Full Mode** to production

**Happy Coding!** 🚀
