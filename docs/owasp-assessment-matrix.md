
# SecureCart OWASP Security Assessment Matrix

## 1. Project Information

**Project:** SecureCart â€“ Web and API Security Assessment

**Framework:** Python Flask

**Database:** SQLite

**Testing Environment:** Authorized local laboratory

**Assessment Date:** 9 October 2026

**Automated Security Tests:** 27 passed

**Verified Findings:** 8 documented and remediated in the tested scenarios

## 2. Introduction

As part of my SecureCart cybersecurity capstone project, I assessed the application's security using the OWASP Web Top 10 (2021) and OWASP API Security Top 10 (2023) as reference frameworks.

I reviewed the application's source code and tested selected API endpoints to identify weaknesses in authentication, authorization, input validation, application configuration, and business logic.

During the assessment, I documented eight security findings and implemented fixes. I also used automated regression tests to verify the corrected behaviors.

This matrix records the security categories I examined, the evidence available, and the areas that still require additional assessment.

## 3. Assessment Status Definitions

- **Finding remediated:** I identified a weakness, implemented a correction, and verified the tested behavior.
- **Partially assessed:** I carried out relevant tests, but the category has not been assessed completely.
- **Not yet assessed:** I have not collected sufficient evidence to evaluate the category.

## 4. OWASP Web Top 10 (2021)

| ID | Security Category | My Assessment and Evidence | Status |
|---|---|---|---|
| A01 | Broken Access Control | I tested restrictions on administrator functions and access to other customers' orders using authorization tests. | Partially assessed |
| A02 | Cryptographic Failures | I identified hardcoded Flask and webhook secrets, replaced them with environment variables, and verified the relevant corrections. SC-001, SC-005. | Finding remediated |
| A03 | Injection | I tested SQL injection-like input in the order creation API and reviewed its parameterized SQL queries. The test passed, but other endpoints still require assessment. | Partially assessed |
| A04 | Insecure Design | I identified weaknesses in order quantity validation, payment-state handling, coupon processing, and inventory management. SC-003, SC-006, SC-007, SC-008. | Partially assessed |
| A05 | Security Misconfiguration | I identified and disabled Flask debug mode. SC-002. | Finding remediated |
| A06 | Vulnerable and Outdated Components | I used pip-audit to scan the Python dependencies in requirements.txt. The scan reported no known vulnerabilities. Evidence: evidence/dependency-audit.txt. Other components have not been fully assessed. | Partially assessed |
| A07 | Identification and Authentication Failures | I tested login behavior and implemented a limit on repeated failed authentication attempts. SC-004. | Partially assessed |
| A08 | Software and Data Integrity Failures | I configured automated tests in GitHub Actions, but have not completed a dedicated software integrity assessment. | Not yet assessed |
| A09 | Security Logging and Monitoring Failures | I used authentication failure events for login rate limiting and reviewed security event functionality. Comprehensive monitoring remains unverified. | Partially assessed |
| A10 | Server-Side Request Forgery (SSRF) | I have not documented dedicated SSRF testing. | Not yet assessed |

## 5. OWASP API Security Top 10 (2023)

| ID | Security Category | My Assessment and Evidence | Status |
|---|---|---|---|
| API1 | Broken Object Level Authorization | I tested whether a customer could access another customer's order. | Partially assessed |
| API2 | Broken Authentication | I identified missing login rate limiting and a hardcoded webhook authentication secret. SC-004, SC-005. | Finding remediated |
| API3 | Broken Object Property Level Authorization | I have not completed a dedicated assessment of unauthorized object property access or modification. | Not yet assessed |
| API4 | Unrestricted Resource Consumption | I implemented a failed-login threshold, but broader API resource-consumption controls remain untested. | Partially assessed |
| API5 | Broken Function Level Authorization | I tested whether customers could access administrator security events or create administrator-managed products. | Partially assessed |
| API6 | Unrestricted Access to Sensitive Business Flows | I identified and corrected improper payment transitions, coupon application after payment, and inventory overselling. SC-006, SC-007, SC-008. | Finding remediated |
| API7 | Server Side Request Forgery | I have not documented dedicated API SSRF testing. | Not yet assessed |
| API8 | Security Misconfiguration | I disabled Flask debug mode and moved sensitive configuration values to environment variables. SC-001, SC-002, SC-005. | Partially assessed |
| API9 | Improper Inventory Management | I have not completed a dedicated assessment of API endpoint inventory, documentation, and version management. | Not yet assessed |
| API10 | Unsafe Consumption of APIs | My application uses mock supplier and payment integrations, but I have not completed a dedicated assessment of unsafe third-party API consumption. | Not yet assessed |

## 6. Verified Security Findings

During my assessment, I documented the following findings:

| Finding ID | Security Weakness | Severity (Provisional) | Remediation |
|---|---|---|---|
| SC-001 | Hardcoded Flask secret key | Medium | Replaced with environment variable |
| SC-002 | Flask debug mode enabled | Medium | Disabled debug mode |
| SC-003 | Improper order quantity validation | Low | Enforced positive integer quantity |
| SC-004 | Missing login rate limiting | Medium | Added database-backed failed-login threshold |
| SC-005 | Hardcoded payment webhook secret | High | Replaced and rotated webhook secret |
| SC-006 | Improper payment status transition | Medium | Rejected invalid transition after payment |
| SC-007 | Coupon applied after payment | Medium | Restricted coupon application to pending orders |
| SC-008 | Inventory overselling | Medium | Added conditional stock deduction within the order transaction |

The detailed reproduction steps, observed results, remediations, and limitations are documented in `docs/security-findings.md`.

## 7. Automated Security Testing

After implementing the security fixes, I ran the automated security tests using Pytest.

I also added a SQL injection security test to check how the SecureCart order creation API handles SQL injection-like input.

I executed:

```powershell
python -m pytest tests/security/ -q
```

My latest local test result was:

```text
........................... [100%]
27 passed in 70.08s (0:01:10)
```

All 27 automated security tests passed successfully.

The SQL injection test confirmed that the order creation endpoint rejected the tested SQL injection-like input. I also reviewed the endpoint's database queries and confirmed that they use parameterized SQL statements.

This provides additional evidence for my OWASP A03:2021 Injection assessment.

My previous GitHub Actions workflow also completed successfully with 26 tests. The newly added 27th test has passed locally but has not yet been verified through GitHub Actions.

**Previous CI evidence:** `evidence/github-actions-success.png`

**Previous successful workflow:** https://github.com/akanbi9/SecureCart/actions/runs/37981063014

## 8. Remaining Security Assessment Activities

Although I remediated the eight documented findings, additional work is necessary to improve the assessment coverage.

Areas requiring further attention include:

- Dedicated injection testing.
- Dependency vulnerability scanning.
- Additional object property authorization tests.
- SSRF testing where applicable.
- API resource-consumption controls.
- API endpoint inventory and version management.
- Security monitoring and alerting verification.
- Mock supplier and payment integration security.
- Broader payment replay and concurrency testing.

## 9. Assessment Limitations

The assessment was performed in an authorized local testing environment using source-code review and targeted security tests.

The OWASP categories were used as a framework for organizing my assessment. A partially assessed category does not mean that every vulnerability within that category has been identified.

Likewise, remediating a documented finding does not establish that the entire OWASP category is secure.

All eight findings were addressed in their documented test scenarios, but some residual risks and production security requirements remain.

## 10. Conclusion

Through my SecureCart security assessment, I gained practical experience identifying application vulnerabilities, implementing security controls, and verifying fixes using automated testing.

I documented eight security findings, corrected the identified weaknesses in their tested scenarios, and successfully executed 26 automated security tests.

I also used GitHub Actions to automate the testing process and provide evidence of successful execution.

The assessment matrix helps me distinguish between completed testing activities and security areas that require further investigation.
