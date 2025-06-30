# Environment Variables

This document explains the environment variables used by ModelSwap.

## Local Development

Create a `.env` file in the root directory with these variables:

```bash
# Development Environment Variables
FLASK_ENV=development
FLASK_DEBUG=true
FLASK_APP=app.py

# Server Configuration
PORT=5000
HOST=0.0.0.0

# Application Settings
MAX_CONTENT_LENGTH=1073741824  # 1GB in bytes
MAX_FILES_PER_REQUEST=10

# Rate Limiting (for development - use memory storage)
# REDIS_URL=redis://localhost:6379  # Uncomment if you have Redis locally

# Logging
LOG_LEVEL=INFO

# Security (for development only)
SECRET_KEY=your-secret-key-here-change-in-production

# File Storage
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
```

## Production (Render)

These variables are automatically set by Render:

```bash
# Production Environment Variables
FLASK_ENV=production
FLASK_DEBUG=false
PORT=5000  # Set by Render

# Optional: Redis for rate limiting (if you add Redis service)
# REDIS_URL=redis://your-redis-url
```

## Environment Variable Details

### Required Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Flask environment | `production` | No |
| `FLASK_DEBUG` | Enable debug mode | `false` | No |
| `PORT` | Server port | `5000` (dev) / `10000` (prod) | No |

### Optional Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_URL` | Redis URL for rate limiting | Memory storage | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `SECRET_KEY` | Flask secret key | Auto-generated | No |
| `MAX_CONTENT_LENGTH` | Max request size (bytes) | `1073741824` (1GB) | No |
| `MAX_FILES_PER_REQUEST` | Max files per upload | `10` | No |

## Setting Up Local Development

1. **Copy the example variables** above to a `.env` file
2. **Install python-dotenv** (if not already installed):
   ```bash
   pip install python-dotenv
   ```
3. **Add to requirements.txt**:
   ```
   python-dotenv==1.0.0
   ```

## Production Deployment

For Render deployment, environment variables are set in the `render.yaml` file:

```yaml
envVars:
  - key: FLASK_ENV
    value: production
  - key: FLASK_DEBUG
    value: false
```

## Security Notes

- **Never commit `.env` files** to version control
- **Use strong secret keys** in production
- **Consider Redis** for rate limiting in production
- **Rotate secrets** regularly 