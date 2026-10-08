
# SecureCart Security Findings Report

## Assessment Overview

Application: SecureCart
Technology: Python Flask and SQLite
Assessment Scope: Web Application and REST API
Testing Environment: Local authorized environment

## Findings Summary

Eight security weaknesses were identified through
source-code review and targeted security testing.

All eight have been remediated in the current
application version.

## SC-001: Hardcoded Flask Secret Key

Severity: Medium (provisional)

Description:
The application originally used a hardcoded Flask
secret key in its source code.

Security Risk:
Disclosure of the secret key could compromise
the integrity of signed Flask sessions.

Remediation:
Replaced the hardcoded secret with the SECRET_KEY
environment variable.

Verification:
Source-code review and successful regression tests.

Status: Remediated

## SC-002: Flask Debug Mode Enabled

Severity: Medium (provisional)

Description:
The Flask development server was configured with
debug mode enabled.

Security Risk:
If exposed to untrusted users, debug functionality
could disclose sensitive information or introduce
serious security risks.

Remediation:
Disabled Flask debug mode.

Verification:
Source-code review.

Status: Remediated

## Remaining Findings


## SC-003: Improper Order Quantity Validation

Severity: Low (provisional)

Description:
The order creation API originally accepted a JSON
boolean value (true) as a valid product quantity.

Affected Endpoint:
POST /api/v1/orders

Security Risk:
Unexpected input types could bypass intended
quantity validation and cause incorrect order
processing.

Steps to Reproduce:
1. Authenticate as a customer.
2. Submit an order containing a valid product_id.
3. Set quantity to the JSON boolean true.
4. Observe that the vulnerable implementation
   accepted the request.

Expected Result:
HTTP 400 Bad Request.

Observed Result Before Remediation:
HTTP 201 Created.

Remediation:
Updated the quantity validation to require an
integer type and a value greater than zero.

Regression Test:
tests/security/test_order_security.py

Verification:
The regression test passed after remediation.

Status: Remediated



## SC-004: Missing Login Rate Limiting

Severity: Medium (provisional)

OWASP Category:
API2:2023 - Broken Authentication

Description:
The SecureCart login API originally allowed repeated
failed login attempts without enforcing a request limit.

Affected Endpoint:
POST /api/v1/auth/login

Security Risk:
An attacker could repeatedly guess account passwords
without being temporarily blocked.

Steps to Reproduce:
1. Open the SecureCart application in the authorized
   local testing environment.
2. Submit five login requests using an existing
   username and an incorrect password.
3. Observe the HTTP responses.

Expected Result:
After three failed attempts, subsequent attempts
should receive HTTP 429 Too Many Requests.

Observed Result Before Remediation:
All five failed login attempts returned HTTP 401
Unauthorized. No rate limit was enforced.

Remediation:
Implemented a database-backed check for recent
failed login attempts.

The application now checks authentication failure
events within a five-minute window and returns
HTTP 429 after the configured threshold is reached.

Regression Test:
tests/security/test_auth_security.py

Verification:
The rate-limiting regression test passed after
remediation.

Limitations:
The current implementation primarily limits
attempts by username. Additional protections,
such as per-IP rate limiting, should be considered
before production deployment.

Status: Remediated in the tested scenario


## SC-005: Hardcoded Payment Webhook Secret

Severity: High (provisional)

OWASP Category:
API2:2023 - Broken Authentication (provisional)

Description:
The SecureCart mock payment webhook originally used
a hardcoded secret stored directly in the application
source code.

Affected Endpoint:
POST /api/v1/webhooks/mock-payment

Security Risk:
Anyone who obtained the hardcoded secret could
submit unauthorized payment notifications.

This could allow an attacker to change order payment
statuses without authorization.

Steps to Reproduce:
1. Inspect the original payment webhook implementation.
2. Identify the hardcoded webhook secret.
3. Submit a payment notification using that secret.
4. Observe the response from the vulnerable version.

Expected Result:
A previously exposed hardcoded secret should not
authorize payment notifications after rotation.

Observed Result Before Remediation:
The webhook accepted the original hardcoded secret
and returned HTTP 200.

Remediation:
Replaced the hardcoded secret with a secret loaded
from the PAYMENT_WEBHOOK_SECRET environment variable.

Generated a new random secret for the local
testing environment.

Regression Test:
tests/security/test_payment_security.py

Verification:
The old hardcoded secret was rejected after
remediation, and the security regression tests passed.

Limitations:
This mock integration uses a shared secret supplied
in the request body. It does not yet implement
production-grade webhook authentication, such as
signed payload verification, timestamps, and
replay protection.

Status: Remediated in the tested scenario



## SC-006: Improper Payment Status Transition

Severity: Medium (provisional)

OWASP Category:
API6:2023 - Unrestricted Access to Sensitive
Business Flows (provisional)

Description:
The SecureCart mock payment webhook originally
allowed an order that was already marked as paid
to be changed to payment_failed.

Affected Endpoint:
POST /api/v1/webhooks/mock-payment

Security Risk:
Improper payment status transitions could cause
inconsistent order records and interfere with
payment processing and order fulfillment.

Steps to Reproduce:
1. Create an order in the authorized local
   testing environment.
2. Submit a valid mock payment notification
   with payment_status set to paid.
3. Submit another valid payment notification
   for the same order with payment_status
   set to failed.
4. Observe the second response.

Expected Result:
The second notification should be rejected
with HTTP 409 Conflict because the order
has already been marked as paid.

Observed Result Before Remediation:
The second notification returned HTTP 200
and changed the order status from paid
to payment_failed.

Remediation:
Added a payment status check before updating
the order.

If an order is already marked as paid, the
webhook now returns HTTP 409 Conflict without
changing the order status.

Regression Test:
tests/security/test_payment_security.py

Verification:
The regression test passed after remediation.

Limitations:
The current implementation does not provide
complete webhook replay protection or enforce
every possible payment state transition.

Status: Remediated in the tested scenario


## SC-007: Coupon Applied After Payment

Severity: Medium (provisional)

OWASP Category:
API6:2023 - Unrestricted Access to Sensitive
Business Flows (provisional)

Description:
The SecureCart coupon API originally allowed a
customer to apply a discount to an order that
had already been marked as paid.

Affected Endpoint:
POST /api/v1/orders/<order_id>/coupon

Security Risk:
Applying discounts after payment could change
the recorded order total without a corresponding
payment adjustment.

This could create inconsistencies between
payment records and order totals.

Steps to Reproduce:
1. Authenticate as a customer.
2. Create an order.
3. Mark the order as paid using an authorized
   mock payment notification.
4. Submit a coupon request using SECURE10.
5. Observe the response.

Expected Result:
HTTP 409 Conflict because the order is
no longer pending.

Observed Result Before Remediation:
The API returned HTTP 200 and accepted
the coupon after payment.

Remediation:
Updated the coupon endpoint to check the
order status before applying the discount.

Coupons can now be applied only when
the order status is pending.

Regression Test:
tests/security/test_coupon_security.py

Verification:
The regression test passed after remediation.

Limitations:
The current implementation checks the order
status before updating the total, but additional
transaction-level safeguards may be needed
to prevent concurrent payment and coupon
operations from causing inconsistencies.

Status: Remediated in the tested scenario



## SC-008: Inventory Overselling Vulnerability

Severity: Medium (provisional)

OWASP Category:
API6:2023 - Unrestricted Access to Sensitive
Business Flows (provisional)

Description:
The SecureCart order creation API originally
checked whether sufficient product stock was
available but did not deduct the purchased
quantity from the inventory.

Affected Endpoint:
POST /api/v1/orders

Security Risk:
A customer could repeatedly create orders for
the same product without reducing its stock.

This could allow the application to accept
more orders than the available inventory
could fulfill.

Steps to Reproduce:
1. Authenticate as a customer.
2. Select a product with available stock.
3. Create an order using the full available
   stock quantity.
4. Create another order for the same product
   using the same quantity.
5. Observe the responses.

Expected Result:
The first order should be accepted, and the
second order should be rejected because
insufficient stock remains.

Observed Result Before Remediation:
Both orders returned HTTP 201 Created.

Remediation:
Updated the order creation endpoint to deduct
the purchased quantity from product inventory.

The application now uses a conditional SQL
UPDATE statement that decreases stock only
when sufficient inventory remains.

The inventory update and order creation are
performed within the same database transaction.

Regression Test:
tests/security/test_order_security.py

Verification:
The regression test passed after remediation.

Limitations:
The current implementation deducts inventory
when an order is created. It does not yet
restore reserved stock when an order is
cancelled or payment fails.

Status: Remediated in the tested scenario


## Testing Summary

Latest completed security test run:
26 tests passed.

Passing automated tests do not guarantee the
absence of other security vulnerabilities.
