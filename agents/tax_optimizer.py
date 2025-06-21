import pandas as pd
from typing import Dict, Any

class TaxOptimizerAgent:
    """
    Computes Indian income tax under both:
      - Old Regime (with 80C up to ₹150k + ₹50k standard deduction)
      - New Regime (no 80C, ₹75k standard deduction + ₹60k rebate), 
        using explicit slab upper-bounds.
    """

    def __init__(self, csv_path: str):
        df = pd.read_csv(csv_path, parse_dates=["Date"])
        self.df = df
        self.gross_income = df.loc[df["Type"] == "Credit", "Amount"].sum()
        # total 80C investments
        self.invest_80c = df.loc[
            (df["Type"] == "Debit") & (df["Category"] == "Investments & Savings"),
            "Amount"
        ].sum()

    def estimate_old_regime(self) -> Dict[str, Any]:
        gross = float(self.gross_income)
        used_80c = min(self.invest_80c, 150_000.0)
        taxable = max(gross - 50_000.0 - used_80c, 0.0)

        tax = 0.0
        remaining = taxable
        old_slabs = [
            (250_000.0, 0.00),
            (500_000.0, 0.05),
            (1_000_000.0, 0.20),
            (float("inf"), 0.30),
        ]
        prev = 0.0
        for upper, rate in old_slabs:
            if taxable <= prev:
                break
            amount = min(taxable, upper) - prev
            tax += amount * rate
            prev = upper

        tax *= 1.04  # 4% cess

        return {
            "regime": "old",
            "gross_income": gross,
            "standard_deduction": 50_000.0,
            "used_80C": used_80c,
            "limit_80C": 150_000.0,
            "taxable_income": taxable,
            "estimated_tax_including_cess": round(tax, 2),
        }

    def estimate_new_regime(self) -> Dict[str, Any]:
        gross = float(self.gross_income)
        # 1) ₹75k standard deduction
        taxable = max(gross - 75_000.0, 0.0)

        # 2) New regime slabs with explicit upper bounds
        tax = 0.0
        new_slabs = [
            (400_000.0, 0.00),     # up to ₹4L
            (800_000.0, 0.05),     # up to ₹8L
            (1_200_000.0, 0.10),   # up to ₹12L
            (1_600_000.0, 0.15),   # up to ₹16L
            (2_000_000.0, 0.20),   # up to ₹20L
            (2_400_000.0, 0.25),   # up to ₹24L
            (float("inf"), 0.30),  # above ₹24L
        ]
        prev = 0.0
        for upper, rate in new_slabs:
            if taxable <= prev:
                break
            amount = min(taxable, upper) - prev
            tax += amount * rate
            prev = upper

        # 3) ₹60k rebate
        tax_after_rebate = max(tax - 60_000.0, 0.0)
        # 4% Health & Education Cess
        tax_with_cess = tax_after_rebate * 1.04

        return {
            "regime": "new",
            "gross_income": gross,
            "standard_deduction": 75_000.0,
            "rebate": 60_000.0,
            "taxable_income": taxable,
            "tax_before_rebate": round(tax, 2),
            "tax_after_rebate": round(tax_after_rebate, 2),
            "estimated_tax_including_cess": round(tax_with_cess, 2),
        }

    def run(self, regime: str = "old") -> Dict[str, Any]:
        """
        :param regime: "old" or "new"
        """
        if regime == "new":
            return {"tax": self.estimate_new_regime()}
        return {"tax": self.estimate_old_regime()}


if __name__ == "__main__":
    import json
    agent = TaxOptimizerAgent("data/structured_transactions.csv")
    print(json.dumps({
        "old_regime": agent.estimate_old_regime(),
        "new_regime": agent.estimate_new_regime()
    }, indent=2))
