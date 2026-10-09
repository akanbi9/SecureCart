
# SecureCart Threat Model

## 1. System Overview

SecureCart is a Flask-based e-commerce application
with a REST API and SQLite database.

It supports customer, support, and administrator roles,
product browsing, order management, coupons,
mock payment notifications, and supplier integration.

## 2. Assets to Protect

| Asset | Security Requirement |
|---|---|
| User accounts | Authentication and authorization |
| Passwords | Secure hashing and confidentiality |
| Session cookies | Integrity and confidentiality |
| Customer profiles | Privacy and access control |
| Orders | Ownership and transaction integrity |
| Product inventory | Accurate stock management |
| Payment statuses | Authorized state transitions |
| Application secrets | Confidentiality and rotation |
| Security logs | Integrity and restricted access |

## 3. Threat Actors

- Unauthenticated external users
- Malicious or compromised customers
- Compromised support accounts
- Compromised administrator accounts
- Attackers with access to leaked application secrets

## 4. Trust Boundaries

Boundary 1: Browser or API client to Flask application.

Boundary 2: Authenticated customer, support, and
administrator permissions.

Boundary 3: Flask application to SQLite database.

Boundary 4: External mock supplier and payment
integration to Flask application.

## 5. Identified Threats

| Threat | Affected Component | Mitigation |
|---|---|---|
| Unauthorized order access | Orders API | Ownership checks |
| Password guessing | Login API | Login attempt limiting |
| Session secret exposure | Flask sessions | Environment-based secret |
| Unauthorized payment updates | Payment webhook | Configured shared secret |
| Invalid payment transitions | Order status | Paid-state protection |
| Coupon misuse | Coupon API | Ownership and status checks |
| Inventory overselling | Orders and products | Conditional stock update |
| Privilege escalation | User profile API | Role modification restrictions |

## 6. Residual Risks

The following areas require additional security
assessment or stronger production controls:

- Comprehensive webhook signature verification
- Webhook replay prevention
- Per-IP and distributed login rate limiting
- Concurrency-safe coupon processing
- Inventory restoration after failed payments
- Production deployment configuration
- Dependency vulnerability monitoring

## 7. Assessment Limitations

This threat model describes the known SecureCart
architecture and previously investigated weaknesses.

It is not a complete penetration test and does
not establish that all threats have been eliminated.
