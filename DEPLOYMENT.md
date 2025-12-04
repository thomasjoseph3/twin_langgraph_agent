# Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker installed (version 20.10+)
- Docker Compose installed (version 1.29+)
- `.env` file configured with your credentials

### Option 1: Using Docker Compose (Recommended)

1. **Ensure `.env` is configured**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

2. **Start the agent**:
   ```bash
   docker-compose up -d
   ```

3. **Interact with the agent**:
   ```bash
   docker-compose exec digital-twin-agent python main.py
   ```

4. **View logs**:
   ```bash
   docker-compose logs -f
   ```

5. **Stop the agent**:
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker CLI

1. **Build the image**:
   ```bash
   docker build -t digital-twin-agent:latest .
   ```

2. **Run the container**:
   ```bash
   docker run -it \
     --env-file .env \
     --name digital-twin-agent \
     digital-twin-agent:latest
   ```

3. **Run with environment variables directly**:
   ```bash
   docker run -it \
     -e GEMINI_API_KEY="your_api_key" \
     -e LLM_MODEL="gemini-2.0-flash-exp" \
     -e PLATFORM_BASE_URL="https://acme.thingspine.com/api" \
     -e TENANT_ID="your_tenant_id" \
     --name digital-twin-agent \
     digital-twin-agent:latest
   ```

### Option 3: Interactive Development

Run the container with mounted source code for development:

```bash
docker run -it \
  --env-file .env \
  -v $(pwd):/app \
  --name digital-twin-agent-dev \
  digital-twin-agent:latest \
  /bin/bash
```

## Production Deployment

### Environment Variables Management

**Never commit `.env` files!** Use secrets management:

#### AWS ECS
Use AWS Secrets Manager:
```json
{
  "GEMINI_API_KEY": {"valueFrom": "arn:aws:secretsmanager:..."},
  "TENANT_ID": {"valueFrom": "arn:aws:secretsmanager:..."}
}
```

#### Kubernetes
Create a secret:
```bash
kubectl create secret generic digital-twin-secrets \
  --from-literal=GEMINI_API_KEY=your_key \
  --from-literal=TENANT_ID=your_tenant_id
```

Reference in deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: digital-twin-agent
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: agent
        image: digital-twin-agent:latest
        envFrom:
        - secretRef:
            name: digital-twin-secrets
```

### Health Checks

The Dockerfile includes a basic health check. Customize based on your needs:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
    CMD python -c "from config import settings; print('healthy')"
```

### Resource Limits

Adjust in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

### Scaling

For horizontal scaling, convert to a REST API (see DEVELOPER_GUIDE.md) and run multiple instances behind a load balancer.

## Troubleshooting

### Container won't start
```bash
docker logs digital-twin-agent
```

### Permission issues
Ensure the container runs as non-root user (already configured in Dockerfile).

### Config not loading
Verify `.env` file is in the same directory when using `--env-file`.

### Memory issues
Increase memory limits in docker-compose.yml or add `--memory` flag to docker run.

## CI/CD Pipeline Example

### GitHub Actions

```yaml
name: Build and Push

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t digital-twin-agent:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push digital-twin-agent:${{ github.sha }}
```

## Monitoring

### Logging

Logs are written to stdout. Collect with:
- Docker logs: `docker logs digital-twin-agent`
- ELK Stack
- CloudWatch (AWS)
- Stackdriver (GCP)

### Metrics

Add Prometheus metrics by installing `prometheus-client` and exposing `/metrics` endpoint.

## Backup & Recovery

### Configuration Backup
- Back up `.env` file securely
- Use version control for code (exclude `.env`)

### State Management
The agent is stateless. No data backup needed unless you add persistence.

## Security Best Practices

1. ✅ **Non-root user**: Container runs as `appuser`
2. ✅ **Minimal base image**: Using `python:3.11-slim`
3. ✅ **Multi-stage build**: Reduces final image size
4. ✅ **No secrets in image**: Environment variables at runtime
5. ✅ **Regular updates**: Rebuild with updated dependencies

## Performance Optimization

1. **Use cached layers**: Requirements are copied first
2. **Minimal dependencies**: Only production packages in requirements.txt
3. **Health checks**: Monitor container health
4. **Resource limits**: Prevent resource exhaustion

## Support

For issues, see DEVELOPER_GUIDE.md troubleshooting section.
