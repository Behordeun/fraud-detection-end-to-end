# Security Policy

## Supported Versions

The following table outlines the versions of the project that are actively supported with security updates and patches:

| Version        | Supported          |
|----------------|--------------------|
| 1.x.x          | ✅ Supported       |
| 0.x.x          | ❌ Unsupported     |

Please ensure you're using the latest version for the most up-to-date security features and fixes.

---

## Reporting a Vulnerability

We take security issues seriously. If you discover a vulnerability, please follow these steps:

1. **Do Not Open a Public Issue**: To protect the project and its users, please do not publicly disclose vulnerabilities.
2. **Send a Detailed Email**:
   - Contact us via email: [security@yourdomain.com](mailto:security@yourdomain.com)
   - Provide:
     - A description of the vulnerability.
     - Steps to reproduce the issue.
     - Potential impact and severity.
     - Any possible fixes or mitigation steps.
3. **Response Timeline**:
   - We will acknowledge receipt of your report within **48 hours**.
   - You will receive updates on the investigation and mitigation process within **7 days**.

---

## Security Best Practices for Contributors

If you're contributing to this project, please adhere to the following security guidelines:

1. **Code Reviews**:
   - Ensure all pull requests are reviewed by at least one other contributor.
   - Check for hardcoded secrets, improper exception handling, and potential SQL injection vulnerabilities.

2. **Secrets Management**:
   - Avoid committing sensitive data (e.g., API keys, passwords, or secrets) to the repository.
   - Use environment variables or secret management tools (e.g., AWS Secrets Manager, HashiCorp Vault).

3. **Dependencies**:
   - Regularly check for vulnerable dependencies using tools like:
     ```bash
     pip install safety
     safety check
     ```
   - Update dependencies to the latest secure versions.

4. **Secure Coding Practices**:
   - Validate user input to prevent injection attacks.
   - Use encryption (e.g., SSL/TLS) for sensitive data transmission.
   - Avoid unnecessary privilege escalation in your code.

---

## Security Features

The project implements the following security features:

- **Data Encryption**:
  - Sensitive data is encrypted during transmission using HTTPS.
- **Access Control**:
  - Role-based access control (RBAC) is used to restrict access to sensitive areas of the application.
- **Audit Logging**:
  - Actions and access to sensitive resources are logged for auditing purposes.

---

## Security Tools Used

We use the following tools to maintain the project's security:

- **Static Code Analysis**: `flake8` and `bandit` for linting and identifying common security issues in Python code.
- **Dependency Scanning**: `safety` and `pip-audit` for identifying vulnerable dependencies.
- **CI/CD Security**:
  - Secrets scanning with GitHub Actions.
  - Dependency caching and isolation in build pipelines.

---

## Responsible Disclosure

If you responsibly disclose a vulnerability, we are committed to:
- **Acknowledging Your Contribution**: Your name or handle will be included in our acknowledgments (if desired).
- **Working Collaboratively**: We aim to fix vulnerabilities as quickly as possible with your input and cooperation.

---

## Contact Us

If you have any questions or concerns regarding the security of this project, feel free to reach out:

- Email: [Email](mailto:smuhammadabiodun@gmail.com)
- GitHub Issues: [Project Repository](https://github.com/behordeun/fraud-detection-end-to-end)
