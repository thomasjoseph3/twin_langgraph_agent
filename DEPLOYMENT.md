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

3. **View logs**:
   ```bash
   docker-compose logs -f digital-twin-agent
   ```

4. **Stop the agent**:
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
   docker run -d \
     -p 8000:8000 \
     --env-file .env \
     --name digital-twin-agent \
     digital-twin-agent:latest
   ```

3. **View logs**:
   ```bash
   docker logs -f digital-twin-agent
   ```

4. **Stop the container**:
   ```bash
   docker stop digital-twin-agent
   docker rm digital-twin-agent
   ```

---

## Verifying the Deployment

### 1. Check Container Status

```bash
# For Docker Compose
docker-compose ps

# For Docker CLI
docker ps | grep digital-twin-agent
```

You should see status as `Up (healthy)` with port mapping `0.0.0.0:8000->8000/tcp`.

### 2. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","service":"Digital Twin AI Agent"}
```

### 3. Test Query Endpoint

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current temperature?",
    "entity_context": {
      "entity_id": 40976504,
      "entity_name": "Heat Exchanger HX00-A3"
    }
  }'
```

### 4. Access Interactive API Documentation

Open in your browser: **http://localhost:8000/docs**

---

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
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: digital-twin-secrets
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

For horizontal scaling, run multiple instances behind a load balancer. The agent is stateless and safe to scale horizontally.

---

## Troubleshooting

### Issue: "Not Found" error when calling API

**Cause**: Missing port mapping in `docker-compose.yml`

**Solution**: Ensure `docker-compose.yml` has the `ports` section:
```yaml
services:
  digital-twin-agent:
    ports:
      - "8000:8000"
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

### Issue: "address already in use" error

**Cause**: Port 8000 is already occupied by another process

**Solution**: Find and stop the conflicting process:
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill <PID>

# Or use a different port in docker-compose.yml:
ports:
  - "8080:8000"  # Map host port 8080 to container port 8000
```

### Issue: ContainerConfig KeyError

**Cause**: Corrupted container state from previous builds

**Solution**: Remove old containers and images:
```bash
docker-compose down
docker rm -f digital-twin-agent 2>/dev/null || true
docker rmi digital-twin-agent:latest 2>/dev/null || true
docker-compose up -d
```

### Issue: Container won't start

**Check logs for errors:**
```bash
docker-compose logs digital-twin-agent
```

**Common issues:**
- Missing `.env` file → Copy from `.env.example`
- Invalid API key → Check `GEMINI_API_KEY` in `.env`
- Permission issues → Container runs as non-root user (already configured)

### Issue: Health check failing

**Verify the application is running:**
```bash
# Check from inside the container
docker-compose exec digital-twin-agent curl http://localhost:8000/health

# Check container logs
docker-compose logs digital-twin-agent | grep ERROR
```

---

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

---

## Monitoring

### Logging

Logs are written to stdout. Collect with:
- Docker logs: `docker logs digital-twin-agent`
- ELK Stack
- CloudWatch (AWS)
- Stackdriver (GCP)

### Metrics

Add Prometheus metrics by installing `prometheus-client` and exposing `/metrics` endpoint.

---

## Backup & Recovery

### Configuration Backup
- Back up `.env` file securely (use secrets manager in production)
- Use version control for code (exclude `.env` from git)

### State Management
The agent is stateless. No data backup needed unless you add persistence.

---

## Security Best Practices

1. ✅ **Non-root user**: Container runs as `appuser`
2. ✅ **Minimal base image**: Using `python:3.11-slim`
3. ✅ **Multi-stage build**: Reduces final image size
4. ✅ **No secrets in image**: Environment variables at runtime
5. ✅ **Regular updates**: Rebuild with updated dependencies
6. ✅ **Port mapping**: Only expose necessary ports

---

## Performance Optimization

1. **Use cached layers**: Requirements are copied first
2. **Minimal dependencies**: Only production packages in requirements.txt
3. **Health checks**: Monitor container health
4. **Resource limits**: Prevent resource exhaustion

---

## Docker Compose Configuration

Your `docker-compose.yml` should include:

```yaml
version: '3.8'

services:
  digital-twin-agent:
    build:
      context: .
      dockerfile: Dockerfile
    image: digital-twin-agent:latest
    container_name: digital-twin-agent
    
    # Port mapping (REQUIRED)
    ports:
      - "8000:8000"
    
    # Environment variables from .env file
    env_file:
      - .env
    
    # Restart policy
    restart: unless-stopped
    
    # Resource limits (optional)
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

---

## Support

- Interactive API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- For detailed development info, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
