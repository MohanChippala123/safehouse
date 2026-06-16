# Security Guidelines

## Reporting Security Issues

If you discover a security vulnerability, please email security@safehouse.local (replace with your actual email) instead of using the issue tracker.

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and work on a fix.

## Security Architecture

### Input Validation
- All URLs validated with `normalize_url()`
- File uploads checked against whitelist
- URL length limited to 2048 characters
- Hostname validation to prevent bypasses

### API Key Protection
- Keys loaded from environment variables only
- Never logged or exposed in errors
- Passed to external APIs over HTTPS only
- Rotate regularly in production

### Network Security
- SSL verification disabled for analysis (intentional - must analyze MITM scenarios)
- HTTPS enforced for external API calls
- Timeouts on all network requests (default 8-10s)
- Connection pooling to prevent exhaustion

### File Handling
- Temporary files created with secure flags
- All temp files deleted after processing
- No persistent storage of uploads
- ExifTool runs in sandbox (subprocess)

### Rate Limiting
- Not implemented in app (use reverse proxy)
- Recommended: CloudFlare, nginx, Render limits
- Per-IP limits: 60 requests/minute recommended
- Per-endpoint throttling: analyze endpoints 10/minute

### Cache Security
- Bounded caches prevent DoS via memory exhaustion
- LOOKUP_CACHE limited to 500 entries
- RESULT_CACHE limited to 200 entries
- Automatic eviction on cap exceeded

## Secure Deployment

### Docker
- Use non-root user (safehouse:safehouse)
- Multi-stage build minimizes final image size
- No pip cache in final image
- Read-only root filesystem (when possible)

### Environment
- Use environment variables for all secrets
- Never commit .env files
- Rotate API keys regularly
- Use strong, unique API keys
- Enable HTTPS at proxy layer

### Database/Storage
- No database (stateless design)
- No persistent storage of analyses
- Temporary files cleaned up automatically
- No sensitive data retained

### Dependencies
- Keep Python 3.12+ updated
- Run `pip check` to find conflicts
- Monitor security advisories
- Update regularly: `pip install --upgrade -r requirements.txt`

## Threat Model

### What We Protect Against
- **Input validation**: Malformed URLs, oversized uploads
- **Memory exhaustion**: Unbounded caches, infinite loops
- **Timeouts**: Hung requests, slow responses
- **API abuse**: Rate limiting (at proxy), throttling
- **Secret exposure**: Environment variables only

### What We Don't Protect Against
- **DDoS**: Use CloudFlare, AWS Shield, etc.
- **Network eavesdropping**: Use TLS at proxy layer
- **Compromised API keys**: Rotate immediately
- **Compromised server**: Assume breach, rotate all secrets
- **Compromised client**: User responsibility

## Best Practices for Users

### Running Locally
- Use Python 3.12+ with latest security patches
- Keep dependencies updated
- Run in isolated network when testing untrusted URLs
- Don't share analysis results with untrusted parties
- Keep API keys in .env, never commit them

### Running in Production
- Use reverse proxy (nginx, CloudFlare) for TLS
- Enable rate limiting at proxy layer
- Use strong authentication (if exposing publicly)
- Monitor logs for anomalies
- Set up alerts for high error rates
- Regularly rotate API keys
- Keep server patched and updated
- Use read-only root filesystem (Docker)
- Enable security headers (CSP, HSTS, X-Frame-Options)

### API Key Management
- Use separate keys for dev/prod
- Rotate keys quarterly (or on suspected compromise)
- Monitor API usage and costs
- Delete unused keys immediately
- Never share keys between services
- Use environment variables only

## Incident Response

### Compromised API Key
1. Revoke immediately in service dashboard
2. Generate new key
3. Update .env in all environments
4. Rotate other keys proactively
5. Review audit logs for misuse
6. Monitor for unusual activity

### Compromised Server
1. Take offline immediately
2. Preserve logs for forensics
3. Rotate all API keys
4. Deploy on clean instance
5. Audit all changes since compromise
6. Monitor for persistence mechanisms

### Bug Report
1. Acknowledge within 48 hours
2. Develop fix in private branch
3. Test thoroughly
4. Release patch
5. Publish disclosure after sufficient time

## Security Checklist

Before deploying to production:

- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS at reverse proxy
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerts
- [ ] Review firewall rules
- [ ] Test input validation
- [ ] Verify no secrets in logs
- [ ] Review dependencies for known CVEs
- [ ] Enable security headers
- [ ] Set up API key rotation schedule
- [ ] Document incident response procedure
- [ ] Train team on security practices

## Security Updates

We follow these practices:
- Security fixes released immediately
- Non-security updates monthly (or as-needed)
- Deprecation policy: 6 months notice
- Long-term support for major versions
- Regular dependency updates

## Compliance

### Data Privacy
- No personal data stored
- Analyses not persisted
- No logging of URLs (except in logs)
- Temporary files cleaned immediately
- GDPR compatible (no data retention)

### Standards
- Input validation per OWASP
- Secure file handling
- Environment-based configuration
- No hardcoded secrets
- Regular security reviews recommended

## Additional Resources

- [OWASP Top 10](https://owasp.org/Top10/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Secure Coding Guidelines](https://www.securecoding.cert.org/)
