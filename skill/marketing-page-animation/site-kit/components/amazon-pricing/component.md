# amazon-pricing

Captured verbatim from `component-library/components/amazon-pricing/`.

- Fields used by the template: 10
- Fields with a blueprint default: 0
- **Template reads fields with no blueprint default:** accountsAdSpendArray, adSpend, enterprise, heroTitle, heroTitleEur, pricingPeriod, savings, subTitle, title, value
- **Copy fields not in the translatable-key list:** accountsAdSpendArray, adSpend, enterprise, pricingPeriod. The script translator (`scripts/translate.js`) matches a field's own key exactly, so it skips these; the LLM localization agent usually translates them anyway. Parity therefore depends on which path runs. Prefer a listed field name for new scene copy, and flag this for the dev team.
- i18n keys: all_prices_are_in, all_prices_for_amazon_advertising_accounts_only, custom, enterprise, full_suite_pricing_available_for_multi_platform_advertisers, on_sale, only_at, per_month_short, terms_and_conditions, whats_your_monthly_ad_spend
