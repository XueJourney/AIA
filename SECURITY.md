# Security Policy

## Overview

AIA (AI Assistant) is a dual-mode conversational AI system that handles sensitive data including API keys, user preferences, and conversation histories. We take security seriously and appreciate the community's help in identifying and addressing security vulnerabilities.

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < 1.0   | :x:                |

## Security Features

### Data Protection
- **API Key Security**: API keys are stored locally using machine-specific hashing
- **Local Storage**: All user data is stored locally, not transmitted to third parties
- **Cache Encryption**: User cache files use machine-specific identifiers
- **Memory Management**: Sensitive data is cleared from memory when possible

### Network Security
- **HTTPS Only**: All API communications use HTTPS endpoints
- **Certificate Validation**: SSL/TLS certificates are validated for all connections
- **No Data Persistence**: Conversations are not stored on remote servers

### Application Security
- **Input Validation**: User inputs are sanitized before processing
- **Error Handling**: Sensitive information is not exposed in error messages
- **Logging**: Debug logs avoid logging sensitive data like API keys

## Known Security Considerations

### API Key Management
- **Local Storage**: API keys are stored in local cache files
- **File Permissions**: Cache files should have restricted permissions (600)
- **Key Rotation**: Users should regularly rotate their API keys

### Third-Party Dependencies
- **OpenAI Client**: Uses official OpenAI Python client
- **Audio Processing**: Relies on pydub and simpleaudio for voice features
- **Network Requests**: Uses requests library for API communications

### Platform-Specific Risks
- **Windows**: Audio files are temporarily stored and played
- **macOS/Linux**: System commands are used for audio playback
- **Cross-Platform**: File system access for cache management

## Reporting Security Vulnerabilities

We take all security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them responsibly:

1. **Email**: Send details to [admin@xuejourney.xin] (admin@xuejourney.xin)
2. **GitHub Security**: Use GitHub's private vulnerability reporting feature
3. **Encrypted Communication**: Use PGP if available for sensitive reports

### What to Include

When reporting a vulnerability, please include:

- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact and attack scenarios
- **Reproduction**: Step-by-step instructions to reproduce
- **Version**: Affected version(s) of AIA
- **Environment**: Operating system and Python version
- **Proof of Concept**: Code or screenshots if applicable

### Response Timeline

- **Acknowledgment**: Within 48 hours of report
- **Initial Assessment**: Within 5 business days
- **Status Updates**: Weekly until resolution
- **Fix Timeline**: Critical issues within 30 days, others within 90 days

## Security Best Practices for Users

### API Key Security
```bash
# Set proper file permissions on cache files
chmod 600 user_cache.json

# Regularly rotate API keys
# Delete old cache files when changing keys
```

### Environment Security
- Keep Python and dependencies updated
- Use virtual environments for isolation
- Avoid running with elevated privileges
- Regularly clear temporary audio files

### Data Protection
- **Sensitive Conversations**: Be cautious with sensitive information
- **Log Files**: Review and rotate log files regularly
- **Cache Management**: Clear cache when sharing systems

## Vulnerability Disclosure Policy

### Coordinated Disclosure
- We follow responsible disclosure practices
- Security researchers are given appropriate time to report
- We coordinate with reporters on disclosure timing
- Public disclosure occurs after fixes are released

### Recognition
- Security researchers will be credited (with permission)
- Serious vulnerabilities may be eligible for recognition
- We maintain a security hall of fame for contributors

## Security Updates

### Notification Channels
- **GitHub Releases**: Security updates noted in release notes
- **Security Advisories**: GitHub security advisories for critical issues
- **Documentation**: Security-related changes documented

### Update Recommendations
- **Automatic Updates**: Consider enabling automatic dependency updates
- **Regular Checks**: Periodically check for security updates
- **Version Pinning**: Pin dependency versions in production

## Development Security Guidelines

### For Contributors
- **Code Review**: All changes require security review
- **Dependency Management**: New dependencies must be security-assessed
- **Testing**: Include security test cases
- **Documentation**: Document security implications of changes

### Secure Coding Practices
```python
# Example: Secure API key handling
def load_api_key():
    # Never log API keys
    key = get_cached_key()
    if not key:
        raise SecurityError("API key not found")
    return key

# Example: Input sanitization
def sanitize_input(user_input):
    # Remove potentially dangerous characters
    return re.sub(r'[<>"\';]', '', user_input.strip())
```

## Third-Party Security

### Dependency Monitoring
- Regular dependency security scans
- Automated vulnerability alerts
- Prompt updates for security issues

### API Provider Security
- **SiliconFlow**: Monitor their security advisories
- **OpenAI Compatible APIs**: Verify provider security practices
- **Voice Services**: Ensure TTS providers follow security standards

## Incident Response

### In Case of Security Incident
1. **Immediate**: Contain the issue and assess impact
2. **Communication**: Notify affected users if necessary
3. **Remediation**: Deploy fixes and security updates
4. **Post-Incident**: Conduct review and improve processes

### User Actions During Incidents
- Update to the latest version immediately
- Rotate API keys if potentially compromised
- Review logs for suspicious activity
- Clear cache files if recommended

## Security Resources

### Documentation
- [Python Security Best Practices](https://python.org/dev/security/)
- [OpenAI API Security](https://platform.openai.com/docs/guides/safety-best-practices)
- [OWASP Python Security](https://owasp.org/www-project-python-security/)

### Tools
- **Static Analysis**: Use bandit for Python security linting
- **Dependency Scanning**: Use safety for dependency vulnerability checks
- **Secrets Detection**: Use git-secrets or similar tools

---

**Last Updated**: December 2024
**Version**: 1.0

For questions about this security policy, please contact the maintainers through the appropriate channels mentioned above.
