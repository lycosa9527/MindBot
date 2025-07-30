# MindBot Docker Deployment Guide / MindBot Docker 部署指南

## 🐳 Overview / 概述

This guide provides comprehensive instructions for deploying MindBot using Docker and Docker Compose. The containerized deployment offers several advantages including consistent environments, easy scaling, and simplified deployment.

本指南提供了使用 Docker 和 Docker Compose 部署 MindBot 的详细说明。容器化部署具有环境一致性、易于扩展和简化部署等优势。

## 📋 Prerequisites / 前置要求

### System Requirements / 系统要求
- **Docker**: Version 20.10+ / 版本 20.10+
- **Docker Compose**: Version 2.0+ / 版本 2.0+
- **Disk Space**: At least 1GB free space / 至少 1GB 可用空间
- **Memory**: At least 512MB RAM / 至少 512MB 内存

### Network Requirements / 网络要求
- **Outbound Access**: Required for DingTalk and Dify APIs / 需要访问钉钉和 Dify API
- **Ports**: No inbound ports required (outbound only) / 无需入站端口（仅出站）

## 🚀 Quick Start / 快速开始

### 1. Clone Repository / 克隆仓库
```bash
git clone https://github.com/lycosa9527/MindBot.git
cd MindBot
```

### 2. Configure Environment / 配置环境
```bash
# Copy environment template
cp config/env_example.txt .env

# Edit environment variables
nano .env
```

### 3. Start with Docker Compose / 使用 Docker Compose 启动
```bash
# Build and start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down
```

## 🔧 Detailed Configuration / 详细配置

### Environment Variables / 环境变量

The following environment variables are supported in the Docker environment:

Docker 环境支持以下环境变量：

#### Required Variables / 必需变量
```bash
# DingTalk Configuration
DINGTALK_CLIENT_ID=your_dingtalk_client_id
DINGTALK_CLIENT_SECRET=your_dingtalk_client_secret
DINGTALK_ROBOT_CODE=your_robot_code

# Dify Configuration
DIFY_API_KEY=your_dify_api_key
DIFY_BASE_URL=your_dify_base_url

# Qwen Configuration
QWEN_API_KEY=your_qwen_api_key
QWEN_BASE_URL=your_qwen_base_url
```

#### Optional Variables / 可选变量
```bash
# DingTalk Optional
DINGTALK_ROBOT_NAME=MindBot_poc
DINGTALK_CARD_TEMPLATE_ID=c497adc7-0d7e-4662-976b-ab07b35332db.schema

# Qwen Optional
QWEN_MODEL=qwen3-0.6b

# Debug Configuration
DEBUG_MODE=false
LOG_LEVEL=INFO

# Streaming Configuration
ENABLE_STREAMING=true
STREAMING_MIN_CHUNK_SIZE=20
STREAMING_UPDATE_DELAY=0.05
STREAMING_MAX_RETRIES=3
STREAMING_RETRY_DELAY=1.0
ENABLE_FLUID_STREAMING=true
FLUID_STREAMING_MIN_CHUNK=10
FLUID_STREAMING_DELAY=0.02
```

### Docker Compose Configuration / Docker Compose 配置

The `docker-compose.yml` file includes:

`docker-compose.yml` 文件包含：

- **Multi-stage build**: Optimized image size
- **Health checks**: Container monitoring
- **Volume mounts**: Persistent logs and config
- **Environment variables**: Flexible configuration
- **Restart policy**: Automatic recovery
- **Logging**: JSON file driver with rotation

## 🛠️ Development Environment / 开发环境

### Local Development / 本地开发
```bash
# Start development environment
docker-compose up

# View real-time logs
docker-compose logs -f mindbot

# Execute commands in container
docker-compose exec mindbot python -c "print('Hello from container')"

# Access container shell
docker-compose exec mindbot bash
```

### Debug Mode / 调试模式
```bash
# Enable debug mode
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG

# Start with debug configuration
docker-compose up
```

## 🚀 Production Deployment / 生产部署

### Production Configuration / 生产配置
```bash
# Create production environment file
cp config/env_example.txt .env.production

# Edit production configuration
nano .env.production

# Start production environment
docker-compose -f docker-compose.yml --env-file .env.production up -d
```

### Scaling / 扩展
```bash
# Scale to multiple instances
docker-compose up -d --scale mindbot=3

# Check running instances
docker-compose ps
```

### Monitoring / 监控
```bash
# View container health
docker-compose ps

# Monitor resource usage
docker stats mindbot-app

# View logs with timestamps
docker-compose logs -f --timestamps mindbot
```

## 🔍 Troubleshooting / 故障排除

### Common Issues / 常见问题

#### 1. Container Won't Start / 容器无法启动
```bash
# Check container logs
docker-compose logs mindbot

# Check environment variables
docker-compose exec mindbot env | grep DINGTALK

# Verify configuration
docker-compose exec mindbot python -c "from src.config import *; print('Config OK')"
```

#### 2. Network Connectivity / 网络连接
```bash
# Test network from container
docker-compose exec mindbot curl -I https://api.dingtalk.com

# Check DNS resolution
docker-compose exec mindbot nslookup api.dingtalk.com
```

#### 3. Permission Issues / 权限问题
```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./logs ./config

# Recreate container
docker-compose down
docker-compose up -d
```

### Debug Commands / 调试命令
```bash
# View detailed container info
docker inspect mindbot-app

# Check container resources
docker stats mindbot-app

# View container processes
docker-compose exec mindbot ps aux

# Check network connectivity
docker-compose exec mindbot ping -c 3 api.dingtalk.com
```

## 📊 Monitoring and Logging / 监控和日志

### Log Management / 日志管理
```bash
# View application logs
docker-compose logs -f mindbot

# View logs with timestamps
docker-compose logs -f --timestamps mindbot

# Export logs to file
docker-compose logs mindbot > mindbot.log

# Clear logs
docker-compose exec mindbot truncate -s 0 /app/logs/*.log
```

### Health Monitoring / 健康监控
```bash
# Check container health
docker-compose ps

# View health check logs
docker inspect mindbot-app | grep -A 10 Health

# Manual health check
docker-compose exec mindbot python -c "import sys; sys.exit(0)"
```

## 🔒 Security Considerations / 安全考虑

### Best Practices / 最佳实践
- **Non-root user**: Container runs as non-root user
- **Read-only mounts**: Environment file mounted as read-only
- **Network isolation**: Container uses isolated network
- **Resource limits**: CPU and memory limits configured
- **Security updates**: Base image regularly updated

### Security Configuration / 安全配置
```bash
# Run with security options
docker run --security-opt=no-new-privileges \
  --cap-drop=ALL \
  --read-only \
  -v /app/logs:/app/logs \
  mindbot
```

## 📈 Performance Optimization / 性能优化

### Resource Limits / 资源限制
```yaml
# Add to docker-compose.yml
services:
  mindbot:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Optimization Tips / 优化技巧
- **Multi-stage builds**: Reduces image size
- **Layer caching**: Optimizes build times
- **Volume mounts**: Persistent storage
- **Health checks**: Automatic recovery
- **Log rotation**: Prevents disk space issues

## 🔄 CI/CD Integration / CI/CD 集成

### GitHub Actions Example / GitHub Actions 示例
```yaml
name: Deploy MindBot

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build and push Docker image
      run: |
        docker build -t mindbot .
        docker push ${{ secrets.DOCKER_REGISTRY }}/mindbot
    
    - name: Deploy to production
      run: |
        docker-compose -f docker-compose.yml --env-file .env.production up -d
```

## 📚 Additional Resources / 其他资源

### Documentation / 文档
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MindBot Wiki](docs/WIKI.md)
- [Voice Recognition Guide](docs/VOICE_RECOGNITION.md)

### Support / 支持
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive guides and examples
- **Community**: Join discussions and share experiences

---

**Last Updated**: January 31, 2025  
**Version**: v0.4.2  
**Maintainer**: MindSpring Team 