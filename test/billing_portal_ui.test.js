const test = require('node:test');
const assert = require('node:assert/strict');

const BillingPortalLogic = require('../web/billing_portal_logic.js');

test('providerLabel normalizes provider names', () => {
  assert.equal(BillingPortalLogic.providerLabel('paypal'), 'PayPal');
  assert.equal(BillingPortalLogic.providerLabel('PayPal'), 'PayPal');
  assert.equal(BillingPortalLogic.providerLabel('stripe'), 'Stripe');
  assert.equal(BillingPortalLogic.providerLabel(''), 'Stripe');
});

test('checkoutButtonText reflects provider and loading state', () => {
  assert.equal(BillingPortalLogic.checkoutButtonText('stripe', false), 'Continue with Stripe');
  assert.equal(BillingPortalLogic.checkoutButtonText('paypal', false), 'Continue with PayPal');
  assert.equal(BillingPortalLogic.checkoutButtonText('paypal', true), 'Redirecting...');
});

test('orderSummaryText includes tier, provider, and estimated amount', () => {
  const summary = BillingPortalLogic.orderSummaryText({
    provider: 'stripe',
    tier: 'premium',
    tierDetails: {
      premium: { amount_usd: 49 },
    },
  });
  assert.match(summary, /PREMIUM/);
  assert.match(summary, /Stripe/);
  assert.match(summary, /\$49\/mo/);
});

test('parseBillingReturn returns success and canceled messages', () => {
  const success = BillingPortalLogic.parseBillingReturn('?billing=success');
  assert.equal(success.kind, 'success');
  assert.match(success.message, /Payment completed successfully/);

  const canceled = BillingPortalLogic.parseBillingReturn('?billing=canceled');
  assert.equal(canceled.kind, 'error');
  assert.match(canceled.message, /Checkout was canceled/);

  const none = BillingPortalLogic.parseBillingReturn('');
  assert.equal(none.kind, 'none');
});
