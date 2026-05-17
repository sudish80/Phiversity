(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  }
  root.BillingPortalLogic = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  function normalizeProvider(provider) {
    return String(provider || '').trim().toLowerCase();
  }

  function providerLabel(provider) {
    var normalized = normalizeProvider(provider);
    if (normalized === 'paypal') {
      return 'PayPal';
    }
    return 'Stripe';
  }

  function toUsd(amount) {
    var value = Number(amount || 0);
    if (!Number.isFinite(value) || value < 0) {
      value = 0;
    }
    return '$' + value + '/mo';
  }

  function tierLabel(tier) {
    return String(tier || 'free').trim().toUpperCase();
  }

  function getTierDetails(tier, allTierDetails) {
    var normalizedTier = String(tier || 'free').trim().toLowerCase();
    var source = allTierDetails || {};
    return source[normalizedTier] || {};
  }

  function orderSummaryText(params) {
    var tier = String((params && params.tier) || 'free').trim().toLowerCase();
    var provider = normalizeProvider(params && params.provider);
    var details = getTierDetails(tier, params && params.tierDetails);
    var amount = Number(details.amount_usd || 0);
    return 'Order summary: ' + tierLabel(tier) + ' via ' + providerLabel(provider) + ' - Estimated ' + toUsd(amount) + '.';
  }

  function redirectingText(params) {
    return orderSummaryText(params) + ' Redirecting to secure checkout...';
  }

  function parseBillingReturn(search) {
    var params = new URLSearchParams(search || '');
    var status = String(params.get('billing') || '').trim().toLowerCase();
    if (status === 'success') {
      return {
        kind: 'success',
        message: 'Payment completed successfully. Your subscription is being synced now.'
      };
    }
    if (status === 'canceled' || status === 'cancelled') {
      return {
        kind: 'error',
        message: 'Checkout was canceled. No charges were applied.'
      };
    }
    return {
      kind: 'none',
      message: ''
    };
  }

  function checkoutButtonText(provider, isLoading) {
    if (isLoading) {
      return 'Redirecting...';
    }
    return 'Continue with ' + providerLabel(provider);
  }

  return {
    checkoutButtonText: checkoutButtonText,
    getTierDetails: getTierDetails,
    orderSummaryText: orderSummaryText,
    parseBillingReturn: parseBillingReturn,
    providerLabel: providerLabel,
    redirectingText: redirectingText,
    tierLabel: tierLabel,
    toUsd: toUsd
  };
});
