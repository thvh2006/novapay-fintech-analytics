# Business Context

NovaPay is a fictional retail-banking case-study company used to frame the analysis. The underlying Berka/PKDD'99 records are historical, anonymised bank data and are never presented as NovaPay customer records.

## Decision questions

1. How quickly do newly opened accounts reach meaningful activity?
2. How are posting activity, customer engagement, and transaction value changing?
3. Which account relationships should receive activation, card-adoption, premium-service, credit-servicing, or risk actions?
4. Where do source coverage and automated ledger postings limit interpretation?

## Stakeholders

- General Manager: portfolio growth, engagement, and overall risk.
- Product and Growth: activation, relationship depth, and feature adoption.
- Operations: posting volume, cash movement, and negative balances.
- Credit Risk: delinquent/defaulted loans and account-level review priorities.

## Definition of done

- Documented public data provenance and limitations.
- Reproducible raw-to-DuckDB pipeline.
- Tested SQL marts and metric definitions.
- Mutually exclusive customer segmentation with explicit actions.
- Executive dashboard, decision memo, and recruiter-readable README.
