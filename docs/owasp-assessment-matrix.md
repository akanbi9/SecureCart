
# SecureCart OWASP Security Assessment Matrix

## Project Information

- Application: SecureCart
- Framework: Python Flask
- Database: SQLite
- Assessment Type: Web and API Security
- Testing Environment: Local authorized laboratory
- Automated Security Tests: 26 passed

## Assessment Scope

This assessment covers the OWASP Web Top 10 (2021)
and OWASP API Security Top 10 (2023).

The assessment evaluates authentication, authorization,
input validation, business logic, payment processing,
inventory management, and security configuration.

## OWASP Web Top 10 (2021)

| ID | Security Category | Assessment Status |
|---|---|---|
| A01 | Broken Access Control | Pending review |
| A02 | Cryptographic Failures | Pending review |
| A03 | Injection | Pending review |
| A04 | Insecure Design | Pending review |
| A05 | Security Misconfiguration | Pending review |
| A06 | Vulnerable and Outdated Components | Pending review |
| A07 | Identification and Authentication Failures | Pending review |
| A08 | Software and Data Integrity Failures | Pending review |
| A09 | Security Logging and Monitoring Failures | Pending review |
| A10 | Server-Side Request Forgery (SSRF) | Pending review |

## OWASP API Security Top 10 (2023)

| ID | Security Category | Assessment Status |
|---|---|---|
| API1 | Broken Object Level Authorization | Pending review |
| API2 | Broken Authentication | Pending review |
| API3 | Broken Object Property Level Authorization | Pending review |
| API4 | Unrestricted Resource Consumption | Pending review |
| API5 | Broken Function Level Authorization | Pending review |
| API6 | Unrestricted Access to Sensitive Business Flows | Pending review |
| API7 | Server Side Request Forgery | Pending review |
| API8 | Security Misconfiguration | Pending review |
| API9 | Improper Inventory Management | Pending review |
| API10 | Unsafe Consumption of APIs | Pending review |

## Verified Security Findings

| Finding ID | Security Weakness | Remediation |
|---|---|---|
| SC-001 | Hardcoded Flask secret key | Fixed |
| SC-002 | Flask debug mode enabled | Fixed |
| SC-003 | Improper order quantity validation | Fixed |
| SC-004 | Missing login rate limiting | Fixed |
| SC-005 | Hardcoded payment webhook secret | Fixed |
| SC-006 | Improper payment status transition | Fixed |
| SC-007 | Coupon applied after payment | Fixed |
| SC-008 | Inventory overselling | Fixed |

## Assessment Notes

The findings above were identified through source-code
review and targeted security testing.

Twenty-six automated security tests passed after the
latest remediation.

Passing tests do not establish that every OWASP category
is fully secure. Each category requires a documented
assessment method and supporting evidence.
