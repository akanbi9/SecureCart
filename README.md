# 🛒 SecureCart — Web Application & API Security Assessment

## 📌 Project Overview

SecureCart is an e-commerce web application developed using Python, Flask, and SQLite as part of a cybersecurity capstone project.

The purpose of this project is to demonstrate how security vulnerabilities can be identified, tested, documented, and remediated in a web application and its APIs.

The assessment is guided by:

- OWASP Top 10:2021 — Web Application Security Risks
- OWASP API Security Top 10:2023
- Secure coding and security testing practices

**Project Repository:** https://github.com/akanbi9/SecureCart

## 🎯 Project Objectives

- Develop a functional e-commerce web application.
- Identify and document web and API security weaknesses.
- Remediate verified vulnerabilities.
- Create automated security regression tests.
- Implement security event logging.
- Use GitHub Actions for Continuous Integration (CI).
- Document the assessment results and remaining risks.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Application database |
| HTML and CSS | Frontend interface |
| pytest | Automated security testing |
| pip-audit | Python dependency vulnerability scanning |
| Git and GitHub | Version control |
| GitHub Actions | Continuous Integration |

## 🛍️ Application Features

SecureCart includes:

- User registration, login, and logout
- Customer, support, and administrator roles
- Product catalogue and search
- Customer profile management
- Order creation and management
- Coupon application
- Administrator product management
- Support functionality
- Mock supplier integration
- Mock payment notifications
- Security event logging

## 🔐 Security Assessment

The project documents eight remediated security findings:

| ID | Security Finding |
|---|---|
| SC-001 | Hardcoded Flask secret key |
| SC-002 | Debug mode enabled |
| SC-003 | Boolean quantity accepted as an integer |
| SC-004 | Missing login rate limiting |
| SC-005 | Hardcoded payment webhook secret |
| SC-006 | Invalid payment status transition |
| SC-007 | Coupon application after payment |
| SC-008 | Product stock not decremented when orders were placed |

The findings, remediation steps, and remaining risks are documented in `docs/security-findings.md`.

## 🧪 Automated Security Testing

SecureCart includes 27 automated security tests covering:

- Authentication and login protection
- Authorization and access control
- Coupon security
- Order input validation
- Stock protection
- SQL injection input handling
- Payment webhook validation
- User role and profile protection

**Latest local test result: 27 passed in 49.21 seconds.**

Run the security tests using:

```bash
python -m pytest tests/security/ -v
```

Passing these tests confirms the tested security behaviors, not that the application is free of all vulnerabilities.

## 🔍 Dependency Vulnerability Assessment

The Python dependencies listed in `requirements.txt` were scanned using `pip-audit`.

```bash
python -m pip_audit -r requirements.txt
```

**Result:** No known vulnerabilities found at the time of the assessment.

Evidence: `evidence/dependency-audit.txt`

This does not cover every possible application component or future vulnerability disclosure.

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/akanbi9/SecureCart.git
cd SecureCart
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Set a strong Flask secret key and payment webhook secret. For a local PowerShell session:

```powershell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
$env:PAYMENT_WEBHOOK_SECRET = python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit actual secret values to GitHub.

### 5. Run the application

```bash
python -m app.app
```

Database initialization and demonstration account setup may require additional local setup depending on the current application configuration.

## 🔄 Continuous Integration

GitHub Actions runs the automated security test suite when changes are pushed to or proposed for the `main` branch.

Workflow: `.github/workflows/security-tests.yml`

Evidence:

- `evidence/github-actions-success.png`
- `evidence/github-actions-27-tests.png`

## 📂 Project Documentation

| Document | Location |
|---|---|
| Security findings | `docs/security-findings.md` |
| OWASP assessment matrix | `docs/owasp-assessment-matrix.md` |
| Threat model | `docs/threat-model.md` |
| Data-flow diagram | `docs/data-flow-diagram.md` |
| Security test results | `docs/security-test-results.md` |
| Final security assessment report | `reports/SecureCart_Final_Security_Assessment_Report.docx` |
| Defense presentation | `reports/SecureCart_Defense_Presentation.pptx` |

## ⚠️ Limitations and Future Improvements

- Complete testing of OWASP categories that are not yet fully assessed.
- Strengthen payment webhook authentication and replay protection.
- Expand dependency and frontend component scanning.
- Improve rate limiting against distributed attacks.
- Extend concurrency and transaction testing.
- Improve deployment security and production readiness.

## 📌 Conclusion

SecureCart demonstrates the practical application of cybersecurity principles to a web application and its APIs.

Through vulnerability assessment, remediation, automated testing, dependency auditing, and CI integration, the project provides hands-on experience with secure software development.

**Disclaimer:** SecureCart is an educational security project. Its mock payment and supplier integrations are not intended for real financial transactions or production deployment.