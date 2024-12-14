# Troubleshooting Guide

This guide helps you diagnose and fix common issues with AIGrok.

## Common Issues

### Installation Issues

#### 1. Package Installation Fails

**Symptoms:**

- `pip install` fails
- Dependency conflicts
- Build errors

**Solutions:**

1. Update pip:

   ```bash
   python -m pip install --upgrade pip
   ```

2. Install in isolated environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install aigrok
   ```

3. Check Python version compatibility:

   ```bash
   python --version  # Should be 3.9+
   ```

#### 2. Ollama Installation Issues

**Symptoms:**

- Model not found
- Connection refused
- API errors

**Solutions:**

1. Verify Ollama installation:

   ```bash
   ollama list
   ```

2. Pull required model:

   ```bash
   ollama pull llama2-vision
   ```

3. Check Ollama service:

   ```bash
   # Linux/macOS
   systemctl status ollama
   
   # or start manually
   ollama serve
   ```

### Runtime Issues

#### 1. Document Processing Fails

**Symptoms:**

- Processing errors
- Timeout errors
- Memory errors

**Solutions:**

1. Check file permissions:

   ```bash
   ls -l document.pdf
   ```

2. Increase timeout:

   ```bash
   aigrok process --timeout 60 document.pdf
   ```

3. Enable low memory mode:

   ```bash
   aigrok process --low-memory document.pdf
   ```

#### 2. Cache Issues

**Symptoms:**

- Cache not working
- Disk space warnings
- Slow performance

**Solutions:**

1. Clear cache:

   ```bash
   aigrok cache clear
   ```

2. Check cache directory:

   ```bash
   ls -lh ~/.cache/aigrok
   ```

3. Configure cache limits:

   ```yaml
   # config.yaml
   cache:
     max_size: "500MB"
     cleanup_interval: 1800
   ```

#### 3. API Connection Issues

**Symptoms:**

- Connection refused
- API timeout
- Authentication errors

**Solutions:**

1. Check Ollama service:

   ```bash
   curl http://localhost:11434/api/version
   ```

2. Verify network settings:

   ```bash
   netstat -an | grep 11434
   ```

3. Check API configuration:

   ```bash
   aigrok config show api
   ```

### Performance Issues

#### 1. Slow Processing

**Symptoms:**

- Long processing times
- High CPU usage
- High memory usage

**Solutions:**

1. Enable caching:

   ```bash
   aigrok process --cache document.pdf
   ```

2. Use batch processing:

   ```bash
   aigrok process --batch-size 5 *.pdf
   ```

3. Monitor resource usage:

   ```bash
   top -p $(pgrep -f aigrok)
   ```

#### 2. Memory Leaks

**Symptoms:**

- Increasing memory usage
- System slowdown
- Out of memory errors

**Solutions:**

1. Enable low memory mode:

   ```yaml
   # config.yaml
   processing:
     low_memory: true
   ```

2. Monitor memory usage:

   ```bash
   watch -n 1 "ps -o pid,ppid,%mem,rss,cmd -p $(pgrep -f aigrok)"
   ```

3. Set memory limits:

   ```bash
   ulimit -v 4000000  # Limit virtual memory to 4GB
   ```

## Debugging

### 1. Enable Debug Logging

```bash
# Command line
aigrok --log-level debug process document.pdf

# Or in config.yaml
logging:
  level: debug
  file: aigrok-debug.log
```

### 2. Check Log Files

```bash
# View logs
tail -f ~/.local/share/aigrok/aigrok.log

# Search for errors
grep ERROR ~/.local/share/aigrok/aigrok.log
```

### 3. Run Diagnostics

```bash
# Check system
aigrok diagnose system

# Check configuration
aigrok diagnose config

# Test API connection
aigrok diagnose api
```

## Error Messages

### Common Error Messages

1. **"Model not found"**
   - Cause: Required AI model not installed
   - Solution: `ollama pull llama2-vision`

2. **"Connection refused"**
   - Cause: Ollama service not running
   - Solution: Start Ollama service

3. **"Out of memory"**
   - Cause: Insufficient system memory
   - Solution: Enable low memory mode or increase system resources

4. **"Permission denied"**
   - Cause: Insufficient file permissions
   - Solution: Check file and directory permissions

## Getting Help

1. **Check Documentation**
   - [CLI Reference](cli.md)
   - [Configuration Guide](configuration.md)
   - [API Documentation](api.md)

2. **Community Support**
   - GitHub Issues
   - Discussion Forums
   - Stack Overflow

3. **Reporting Bugs**
   - Include error messages
   - Attach log files
   - Describe reproduction steps