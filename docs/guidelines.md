# Aigrok Development Guidelines

## Core Principles
- Use `ConfigManager` for all configuration management
- Never commit sensitive data (API keys, credentials)
- Write tests for new functionality
- Document significant changes

## Code Organization
- Keep provider-specific code in separate methods
- Use type hints consistently
- Use pydantic models for data validation
- Follow existing class structures

## Implementation Guidelines

### Configuration
```python
# Good
from aigrok.config import ConfigManager
config = ConfigManager()
api_key = config.get_api_key("provider_name")

# Bad
api_key = "hardcoded_key"  # Never do this
```

### Error Handling
- Use specific exception types
- Log errors with `loguru`
- Provide clear error messages
```python
try:
    response = await provider.generate()
except ProviderAPIError as e:
    logger.error(f"Provider API error: {e}")
    raise UserFacingError("Service temporarily unavailable")
```

### Model Management
- Validate model capabilities before use
- Handle Ollama models as dynamic resources
- Consider costs and capabilities in model selection

### Testing
```python
def test_provider_integration():
    """Test core provider functionality"""
    # Test happy path
    # Test error cases
    # Test rate limiting
```

### Performance Best Practices
- Cache model lists and configurations
- Use async where appropriate
- Minimize API calls
- Handle large files efficiently

### Documentation
- Keep docstrings current
- Document provider-specific behaviors
- Include examples for complex features

### Code Changes
1. Update spec first (if needed)
2. Implement changes
3. Add/update tests
4. Update documentation
5. Update HISTORY.md for significant changes
