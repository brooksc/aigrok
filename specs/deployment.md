# Deployment Guide

## Overview

This guide covers deployment options and best practices for AIGrok in various environments.

## Local Deployment

### System Requirements

- Python 3.9+
- 4GB RAM minimum
- 2GB disk space
- Internet connection for API access

### Installation Steps

1. Install from PyPI:

   ```bash
   pip install aigrok
   ```

2. Create configuration directory:

   ```bash
   mkdir -p ~/.config/aigrok
   ```

3. Create configuration file:

   ```bash
   cat > ~/.config/aigrok/config.yaml << EOL
   models:
     text:
       default: "gpt-3.5-turbo"
       fallback: "ollama/llama2"
     vision:
       default: "gpt-4-vision"
       fallback: "claude-3-opus"
   EOL
   ```

4. Set environment variables:

   ```bash
   export AIGROK_MODEL="gpt-4-vision"
   export AIGROK_FORMAT="text"
   ```

## Docker Deployment

### Docker Image

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install aigrok
RUN pip install aigrok

# Copy configuration
COPY config.yaml /root/.config/aigrok/config.yaml

# Set environment variables
ENV AIGROK_MODEL="gpt-4-vision"
ENV AIGROK_FORMAT="text"

# Run command
ENTRYPOINT ["aigrok"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  aigrok:
    build: .
    volumes:
      - ./data:/data
      - ./config:/root/.config/aigrok
    environment:
      - AIGROK_MODEL=gpt-4-vision
      - AIGROK_FORMAT=text
```

### Running with Docker

```bash
# Build image
docker build -t aigrok .

# Run container
docker run -v $(pwd)/data:/data aigrok "Extract text" /data/document.pdf
```

## Cloud Deployment

### AWS Deployment

#### Lambda Function

```python
import json
from aigrok import process_document

def lambda_handler(event, context):
    """AWS Lambda handler for AIGrok processing."""
    try:
        file_path = event['file_path']
        prompt = event.get('prompt', 'Extract text')
        
        result = process_document(file_path, prompt)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': result.success,
                'text': result.text,
                'error': result.error
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
```

#### ECS Service

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  AIGrokService:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref AIGrokTaskDefinition
      DesiredCount: 1
      
  AIGrokTaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: aigrok
      ContainerDefinitions:
        - Name: aigrok
          Image: aigrok:latest
          Memory: 2048
          Environment:
            - Name: AIGROK_MODEL
              Value: gpt-4-vision
```

### Google Cloud Deployment

#### Cloud Run

```yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/aigrok', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/aigrok']
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  entrypoint: gcloud
  args:
  - 'run'
  - 'deploy'
  - 'aigrok'
  - '--image'
  - 'gcr.io/$PROJECT_ID/aigrok'
  - '--platform'
  - 'managed'
```

### Azure Deployment

#### Azure Container Instance

```bash
# Create resource group
az group create --name aigrok-rg --location eastus

# Create container instance
az container create \
    --resource-group aigrok-rg \
    --name aigrok \
    --image aigrok:latest \
    --dns-name-label aigrok \
    --ports 80
```

## Monitoring & Logging

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aigrok.log'),
        logging.StreamHandler()
    ]
)
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

REQUESTS = Counter('aigrok_requests_total', 'Total requests')
PROCESSING_TIME = Histogram('aigrok_processing_seconds', 'Processing time')
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "id": null,
    "title": "AIGrok Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(aigrok_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

## Security

### API Key Management

1. Use environment variables:

   ```bash
   export OPENAI_API_KEY="sk-..."
   export ANTHROPIC_API_KEY="sk-..."
   ```

2. Use secrets management:

   ```python
   from azure.keyvault.secrets import SecretClient
   
   def get_api_key(key_name: str) -> str:
       """Get API key from Azure Key Vault."""
       client = SecretClient(vault_url=VAULT_URL, credential=credential)
       return client.get_secret(key_name).value
   ```

### Network Security

1. Configure firewall rules:

   ```bash
   # Allow only necessary ports
   ufw allow 80/tcp
   ufw allow 443/tcp
   ```

2. Use VPC for cloud deployments:

   ```yaml
   Resources:
     AIGrokVPC:
       Type: AWS::EC2::VPC
       Properties:
         CidrBlock: 10.0.0.0/16
         EnableDnsSupport: true
         EnableDnsHostnames: true
   ```

## Scaling

### Horizontal Scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: aigrok-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: aigrok
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

### Rate Limiting

```python
from fastapi import FastAPI, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

app = FastAPI()

@app.post("/process")
@RateLimiter(times=60, seconds=60)
async def process_document():
    """Process document with rate limiting."""
    pass
```

## Backup & Recovery

### Backup Configuration

```bash
#!/bin/bash

# Backup configuration
backup_dir="/backups/aigrok"
date_stamp=$(date +%Y%m%d_%H%M%S)

# Create backup
tar -czf "$backup_dir/config_$date_stamp.tar.gz" ~/.config/aigrok/
```

### Recovery Procedure

1. Stop service:

   ```bash
   systemctl stop aigrok
   ```

2. Restore configuration:

   ```bash
   tar -xzf backup.tar.gz -C /
   ```

3. Restart service:

   ```bash
   systemctl start aigrok
   ```

## Maintenance

### Health Checks

```python
from fastapi import FastAPI
from aigrok import health_check

app = FastAPI()

@app.get("/health")
async def health():
    """Health check endpoint."""
    status = health_check()
    return {"status": "healthy" if status else "unhealthy"}
```

### Database Maintenance

```sql
-- Clean up old processing records
DELETE FROM processing_history
WHERE created_at < NOW() - INTERVAL '30 days';

-- Optimize tables
VACUUM ANALYZE processing_history;
```

### Log Rotation

```conf
/var/log/aigrok/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 aigrok aigrok
}
```