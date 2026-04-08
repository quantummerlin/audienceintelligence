# OpenClaw Security Hardening Checklist
## Fix the 2,000 CVEs & Secure Your Deployment

---

## ⚠️ The Hard Truth

The official OpenClaw Docker image ships with approximately **2,000 known CVEs** (Common Vulnerabilities and Exposures). This means:

- Your API keys can be exposed in plaintext logs
- Malicious ClawHub skills can execute system commands
- Gateways are exposed to the internet by default
- Filesystem access is unrestricted

**This checklist will help you secure your deployment.**

---

## Pre-Deployment Security Checklist

### 🔴 CRITICAL (Do Before First Run)

- [ ] **Scan the official image for CVEs**
  ```bash
  docker pull openclaw/openclaw:latest
  docker scout cves openclaw/openclaw:latest
  # OR
  trivy image openclaw/openclaw:latest
  ```

- [ ] **Build a minimal custom image**
  ```dockerfile
  FROM python:3.11-slim
  
  # Install only required dependencies
  RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
      curl \
      && rm -rf /var/lib/apt/lists/*
  
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  
  COPY . .
  
  # Run as non-root user
  RUN useradd -m -u 1000 openclaw && chown -R openclaw:openclaw /app
  USER openclaw
  
  CMD ["python", "-m", "openclaw"]
  ```

- [ ] **Never run as root**
  ```yaml
  # docker-compose.yml
  services:
    openclaw:
      user: "1000:1000"
      read_only: true  # Prevent filesystem modifications
  ```

- [ ] **Store API keys in secrets, not environment variables**
  ```yaml
  # docker-compose.yml
  services:
    openclaw:
      secrets:
        - openai_api_key
        - anthropic_api_key
  
  secrets:
    openai_api_key:
      file: ./secrets/openai_api_key.txt
    anthropic_api_key:
      file: ./secrets/anthropic_api_key.txt
  ```

- [ ] **Set file permissions on secrets**
  ```bash
  mkdir -p secrets
  echo "sk-your-key-here" > secrets/openai_api_key.txt
  chmod 600 secrets/*
  ls -la secrets/
  # Should show: -rw------- 1 user user
  ```

---

### 🟠 HIGH PRIORITY (Do Within 24 Hours)

- [ ] **Restrict filesystem access**
  ```yaml
  # docker-compose.yml
  services:
    openclaw:
      volumes:
        - ./workspace:/workspace:rw  # Only workspace is writable
      tmpfs:
        - /tmp:noexec,nosuid,size=100m
  ```

- [ ] **Block outbound connections to sensitive endpoints**
  ```yaml
  # docker-compose.yml
  services:
    openclaw:
      network_mode: "bridge"
      extra_hosts:
        - "metadata.google.internal:127.0.0.1"  # Block GCP metadata
        - "169.254.169.254:127.0.0.1"  # Block AWS/Azure metadata
  ```

- [ ] **Disable unnecessary network ports**
  ```yaml
  # Only expose what you need
  services:
    openclaw:
      ports:
        - "127.0.0.1:8080:8080"  # Bind to localhost only
      expose:
        - "8080"
  ```

- [ ] **Add authentication to gateway**
  ```yaml
  # In your agent config
  gateway:
    auth:
      enabled: true
      type: "bearer"
      token: "${GATEWAY_AUTH_TOKEN}"
  ```

- [ ] **Enable audit logging**
  ```yaml
  logging:
    level: INFO
    format: json
    output: /var/log/openclaw/audit.log
    audit:
      enabled: true
      log_commands: true
      log_file_access: true
  ```

---

### 🟡 MEDIUM PRIORITY (Do Within 1 Week)

- [ ] **Implement network segmentation**
  ```yaml
  # docker-compose.yml
  networks:
    openclaw_internal:
      driver: bridge
      internal: true  # No external internet access
    openclaw_api:
      driver: bridge
  
  services:
    openclaw:
      networks:
        - openclaw_internal
        - openclaw_api
  
    # Separate proxy for external access
    nginx:
      image: nginx:alpine
      networks:
        - openclaw_api
      ports:
        - "443:443"
  ```

- [ ] **Set up a reverse proxy with TLS**
  ```nginx
  # nginx.conf
  server {
      listen 443 ssl http2;
      server_name openclaw.yourdomain.com;
  
      ssl_certificate /etc/nginx/ssl/cert.pem;
      ssl_certificate_key /etc/nginx/ssl/key.pem;
      ssl_protocols TLSv1.2 TLSv1.3;
      ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
  
      location / {
          proxy_pass http://openclaw:8080;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }
  ```

- [ ] **Configure rate limiting**
  ```yaml
  # In agent config
  rate_limit:
    requests_per_minute: 60
    tokens_per_minute: 100000
    burst_allowance: 10
  ```

- [ ] **Set up container health checks**
  ```yaml
  # docker-compose.yml
  services:
    openclaw:
      healthcheck:
        test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
        interval: 30s
        timeout: 10s
        retries: 3
        start_period: 40s
  ```

- [ ] **Enable automatic security updates**
  ```bash
  # Watch for new CVEs
  docker scout watch openclaw/openclaw:latest
  ```

---

### 🟢 ONGOING (Weekly/Monthly)

- [ ] **Weekly CVE scan**
  ```bash
  # Add to crontab
  0 2 * * 0 docker scout cves openclaw/openclaw:latest > /var/log/openclaw-cves.log
  ```

- [ ] **Monthly dependency updates**
  ```bash
  pip-audit  # Check Python dependencies
  npm audit   # If using Node.js components
  ```

- [ ] **Rotate API keys quarterly**
  ```bash
  # Generate new keys, update secrets, revoke old ones
  ```

- [ ] **Review audit logs**
  ```bash
  grep -i "unauthorized\|failed\|error" /var/log/openclaw/audit.log
  ```

- [ ] **Backup and test restore**
  ```bash
  # Backup
  docker exec openclaw tar czf - /data > backup-$(date +%Y%m%d).tar.gz
  
  # Test restore (on separate instance)
  docker exec -i openclaw-test tar xzf - -C / < backup-20240115.tar.gz
  ```

---

## ClawHub Skills Security Checklist

### Before Installing Any Skill

- [ ] **Check the source repository**
  ```bash
  # Who owns it? How many stars? Recent commits?
  gh repo view <skill-repo>
  ```

- [ ] **Review the code manually**
  ```bash
  # Look for suspicious patterns
  grep -r "subprocess\|exec\|eval\|os.system\|__import__" <skill-dir>/
  grep -r "requests\|urllib\|http\|socket" <skill-dir>/
  grep -r "open(\|write(\|remove(\|unlink(" <skill-dir>/
  ```

- [ ] **Check for network calls**
  ```bash
  # Should only call known APIs
  grep -r "https://" <skill-dir>/ | grep -v "api.openai\|api.anthropic"
  ```

- [ ] **Check for filesystem access**
  ```bash
  # Should only access designated directories
  grep -r "open(" <skill-dir>/ | grep -v "/workspace\|/tmp"
  ```

- [ ] **Check for credential access**
  ```bash
  # Should not read environment variables or secret files
  grep -r "os.environ\|getenv\|API_KEY\|SECRET\|PASSWORD" <skill-dir>/
  ```

### High-Risk Patterns to Watch For

| Pattern | Risk Level | What It Means |
|---------|------------|---------------|
| `subprocess.run(..., shell=True)` | 🔴 CRITICAL | Can execute arbitrary commands |
| `eval(user_input)` | 🔴 CRITICAL | Remote code execution |
| `requests.post(external_url, data=...)` | 🔴 HIGH | Data exfiltration |
| `open("/etc/passwd")` or `/etc/shadow` | 🔴 CRITICAL | Credential theft |
| `os.environ.get("AWS_SECRET")` | 🔴 HIGH | Accessing secrets |
| `socket.connect(...)` | 🟠 MEDIUM | Direct network connection |
| `pickle.loads(user_data)` | 🔴 CRITICAL | Code execution via pickle |
| `yaml.load(user_input)` without `Loader` | 🔴 HIGH | YAML deserialization attack |

### Safe Skill Installation Process

```bash
# 1. Download but don't install
git clone <skill-repo> /tmp/skill-audit

# 2. Run security scan
cd /tmp/skill-audit
semgrep --config auto .

# 3. Review findings
# 4. If clean, copy to skills directory
cp -r /tmp/skill-audit /path/to/openclaw/skills/

# 5. Set restrictive permissions
chmod -R 555 /path/to/openclaw/skills/skill-audit  # Read + execute only
```

---

## Hardened Docker Compose Template

```yaml
version: "3.9"

secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt
  anthropic_api_key:
    file: ./secrets/anthropic_api_key.txt
  gateway_auth_token:
    file: ./secrets/gateway_token.txt

networks:
  openclaw_internal:
    driver: bridge
    internal: true
  openclaw_public:
    driver: bridge

services:
  openclaw:
    build:
      context: .
      dockerfile: Dockerfile.hardened
    user: "1000:1000"
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
    secrets:
      - openai_api_key
      - anthropic_api_key
      - gateway_auth_token
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key
      - ANTHROPIC_API_KEY_FILE=/run/secrets/anthropic_api_key
    volumes:
      - ./workspace:/workspace:rw
      - ./config:/app/config:ro
    networks:
      - openclaw_internal
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    security_opt:
      - no-new-privileges:true
      - apparmor:docker-default
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    ports:
      - "127.0.0.1:443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - openclaw_public
      - openclaw_internal
    depends_on:
      - openclaw
    restart: unless-stopped
```

---

## Security Incident Response

### If You Suspect a Breach

1. **Immediately rotate all API keys**
   ```bash
   # OpenAI
   curl -X DELETE "https://api.openai.com/v1/api-keys/{key_id}" \
     -H "Authorization: Bearer $OPENAI_ADMIN_KEY"
   
   # Generate new key and update secrets
   ```

2. **Stop the container**
   ```bash
   docker-compose down
   ```

3. **Preserve logs for investigation**
   ```bash
   docker logs openclaw > incident-$(date +%Y%m%d-%H%M%S).log
   cp -r /var/log/openclaw incident-logs/
   ```

4. **Check for unauthorized access**
   ```bash
   # Check API usage
   curl https://api.openai.com/v1/usage \
     -H "Authorization: Bearer $OPENAI_ADMIN_KEY"
   
   # Check for unusual patterns
   grep -i "error\|unauthorized\|failed" incident-logs/audit.log
   ```

5. **Audit installed skills**
   ```bash
   ls -la /path/to/openclaw/skills/
   git -C /path/to/openclaw/skills/ status  # Check for modifications
   ```

6. **Report and document**
   - Document timeline of events
   - Identify attack vector
   - Update security measures
   - Consider reporting to OpenClaw maintainers

---

## Quick Security Score

Rate your deployment:

| Check | Points | Your Score |
|-------|--------|------------|
| Running as non-root | 10 | ___ |
| API keys in secrets | 10 | ___ |
| Filesystem restricted | 10 | ___ |
| Network segmented | 10 | ___ |
| TLS enabled | 10 | ___ |
| Authentication enabled | 10 | ___ |
| Audit logging enabled | 10 | ___ |
| CVE scanning in CI/CD | 10 | ___ |
| Skills manually reviewed | 10 | ___ |
| Budget caps in place | 10 | ___ |
| **TOTAL** | **100** | ___ |

**Score Interpretation:**
- 90-100: Well hardened
- 70-89: Good, room for improvement
- 50-69: Significant gaps, prioritize fixes
- Below 50: Critical vulnerabilities, do not deploy to production

---

## Resources

- [Docker Security Documentation](https://docs.docker.com/engine/security/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [Trivy Vulnerability Scanner](https://github.com/aquasecurity/trivy)
- [Semgrep Security Scanner](https://semgrep.dev/)

---

*Last updated: 2024. Security is an ongoing process. Review this checklist monthly.*