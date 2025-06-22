import pandas as pd
from datetime import datetime
from typing import Dict, Any

class BudgetingAgent:
    """
    Reads structured_transactions.csv and provides:
      - Total income, expenses, savings
      - Expense breakdown by category
      - Monthly credit/debit/savings summary
      - A simple savings recommendation
    """

    def __init__(self, csv_path: str):
        # 1) Load CSV
        self.df = pd.read_csv(csv_path)

        # 2) Ensure 'Date' exists
        if 'Date' not in self.df.columns:
            raise ValueError("CSV must include a 'Date' column")

        # 3) Parse 'Date' into datetime, drop unparseable rows
        self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
        self.df = self.df.dropna(subset=['Date'])

        # 4) Normalize 'Type' and compute 'Month'
        self.df['Type'] = self.df['Type'].str.capitalize()
        # .dt accessor is now safe because 'Date' is datetime
        self.df['Month'] = self.df['Date'].dt.to_period('M')

    def compute_totals(self) -> Dict[str, float]:
        income = self.df.loc[self.df['Type'] == 'Credit', 'Amount'].sum()
        expense = self.df.loc[self.df['Type'] == 'Debit', 'Amount'].sum()
        savings = income - expense
        return {
            'total_income': float(income),
            'total_expense': float(expense),
            'savings': float(savings)
        }

    def category_summary(self) -> pd.Series:
        # Only expenses, grouped by Category
        return (
            self.df[self.df['Type'] == 'Debit']
            .groupby('Category')['Amount']
            .sum()
            .sort_values(ascending=False)
        )

    def monthly_summary(self) -> pd.DataFrame:
        # Pivot by Month & Type, fill missing, compute savings
        monthly = (
            self.df
            .groupby(['Month', 'Type'])['Amount']
            .sum()
            .unstack(fill_value=0)
        )
        monthly['Savings'] = monthly.get('Credit', 0) - monthly.get('Debit', 0)
        # Convert Period index to string for JSON serialization
        monthly = monthly.reset_index()
        monthly['Month'] = monthly['Month'].astype(str)
        return monthly

    def recommend_savings(self) -> Dict[str, Any]:
        cat = self.category_summary()
        if cat.empty:
            return {
                'suggestion': "No expense data available to generate recommendations."
            }

        top_cat = cat.index[0]
        top_amt = float(cat.iloc[0])
        totals = self.compute_totals()
        expense = totals['total_expense']

        pct = (top_amt / expense * 100) if expense else 0
        potential_saving = top_amt * 0.2

        suggestion = (
            f"You spend {pct:.1f}% of your expenses on {top_cat}. "
            f"Cutting that by 20% could save you ₹{potential_saving:.2f}."
        )
        return {
            'top_category': top_cat,
            'top_amount': top_amt,
            'top_pct': pct,
            'suggestion': suggestion
        }

    def run(self) -> Dict[str, Any]:
        return {
            'totals': self.compute_totals(),
            'category_expenses': self.category_summary().to_dict(),
            'monthly_summary': self.monthly_summary().to_dict(orient='records'),
            'recommendation': self.recommend_savings()
        }

if __name__ == '__main__':
    import json
    agent = BudgetingAgent('data/structured_transactions.csv')
    result = agent.run()
    print(json.dumps(result, indent=2, default=str))
