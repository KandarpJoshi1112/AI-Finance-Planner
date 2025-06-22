import pandas as pd
from typing import Dict, Any

class TaxOptimizerAgent:
    """
    Computes Indian income tax under both:
      - Old Regime: allows 80C (up to ₹1.5L) + ₹50k standard deduction + ₹12.5k rebate if TI ≤ ₹5L
      - New Regime: no 80C + ₹75k standard deduction + ₹60k rebate if TI ≤ ₹12L
    """

    def __init__(self, csv_path: str):
        df = pd.read_csv(csv_path, parse_dates=["Date"])
        self.df = df
        self.gross = float(df.loc[df["Type"] == "Credit", "Amount"].sum())
        # total invested under 80C-eligible categories
        self.used_80c = float(df.loc[
            (df["Type"] == "Debit") &
            (df["Category"] == "Investments & Savings"),
            "Amount"
        ].sum())

    def estimate_old_regime(self) -> Dict[str, Any]:
        STD_DED = 50_000.0
        LIMIT_80C = 150_000.0
        REBATE_THRESH = 500_000.0   # TI ≤ 5L
        REBATE_LIMIT = 12_500.0     # max rebate

        used80 = min(self.used_80c, LIMIT_80C)
        rem80 = max(LIMIT_80C - used80, 0.0)
        taxable = max(self.gross - STD_DED - used80, 0.0)

        # slab computation with upper bounds
        slabs = [
            (250_000.0, 0.00),
            (500_000.0, 0.05),
            (1_000_000.0, 0.20),
            (float("inf"),  0.30),
        ]
        tax = 0.0
        prev = 0.0
        for upper, rate in slabs:
            if taxable <= prev:
                break
            portion = min(taxable, upper) - prev
            tax += portion * rate
            prev = upper

        tax_before_cess = tax
        tax_with_cess  = tax * 1.04

        # Section 87A rebate
        rebate = REBATE_LIMIT if taxable <= REBATE_THRESH else 0.0
        rebate = min(rebate, tax_with_cess)
        rem_rebate = max(REBATE_THRESH - taxable, 0.0)

        tax_after_rebate = max(tax_with_cess - rebate, 0.0)

        return {
            "regime": "old",
            "gross_income": self.gross,
            "standard_deduction": STD_DED,
            "used_80C": used80,
            "remaining_80C": rem80,
            "limit_80C": LIMIT_80C,
            "taxable_income": taxable,
            "tax_before_cess": round(tax_before_cess, 2),
            "tax_with_cess": round(tax_with_cess, 2),
            "rebate_threshold": REBATE_THRESH,
            "rebate_limit": REBATE_LIMIT,
            "rebate_applied": round(rebate, 2),
            "remaining_for_rebate": round(rem_rebate, 2),
            "tax_after_rebate": round(tax_after_rebate, 2),
        }

    def estimate_new_regime(self) -> Dict[str, Any]:
        STD_DED = 75_000.0
        REBATE_THRESH = 1_200_000.0  # TI ≤ 12L
        REBATE_LIMIT = 60_000.0      # max rebate

        used80 = 0.0
        rem80 = 0.0
        taxable = max(self.gross - STD_DED, 0.0)

        slabs = [
            (400_000.0, 0.00),
            (800_000.0, 0.05),
            (1_200_000.0, 0.10),
            (1_600_000.0, 0.15),
            (2_000_000.0, 0.20),
            (2_400_000.0, 0.25),
            (float("inf"), 0.30),
        ]
        tax = 0.0
        prev = 0.0
        for upper, rate in slabs:
            if taxable <= prev:
                break
            portion = min(taxable, upper) - prev
            tax += portion * rate
            prev = upper

        tax_before_rebate = tax
        tax_after_rebate = max(tax - REBATE_LIMIT if taxable <= REBATE_THRESH else tax, 0.0)
        tax_with_cess = tax_after_rebate * 1.04
        rem_rebate = max(REBATE_THRESH - taxable, 0.0)

        return {
            "regime": "new",
            "gross_income": self.gross,
            "standard_deduction": STD_DED,
            "used_80C": used80,
            "remaining_80C": rem80,
            "limit_80C": 0.0,
            "taxable_income": taxable,
            "tax_before_rebate": round(tax_before_rebate, 2),
            "rebate_threshold": REBATE_THRESH,
            "rebate_limit": REBATE_LIMIT,
            "rebate_applied": round(min(tax_before_rebate, REBATE_LIMIT) if taxable <= REBATE_THRESH else 0.0, 2),
            "remaining_for_rebate": round(rem_rebate, 2),
            "tax_after_rebate": round(tax_with_cess, 2),
        }

    def run(self, regime: str = "old") -> Dict[str, Any]:
        return {
            "tax": self.estimate_new_regime() if regime == "new"
                   else self.estimate_old_regime()
        }


if __name__ == "__main__":
    import json
    ag = TaxOptimizerAgent("data/structured_transactions.csv")
    print(json.dumps({
        "old_regime": ag.estimate_old_regime(),
        "new_regime": ag.estimate_new_regime()
    }, indent=2))
