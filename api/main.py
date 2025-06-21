from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agents.budgeting_agent import BudgetingAgent
from agents.tax_optimizer import TaxOptimizerAgent
app = FastAPI(title="AI Finance Planner API")

# Allow your frontend (e.g., http://localhost:3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/budget-summary")
def budget_summary():
    """
    Returns totals, category breakdown, monthly summary,
    and a savings recommendation.
    """
    agent = BudgetingAgent("data/structured_transactions.csv")
    return agent.run()

@app.get("/tax-summary")
def tax_summary(regime: str = "old"):
    agent = TaxOptimizerAgent("data/structured_transactions.csv")
    return agent.run(regime)

@app.get("/")
def root():
    return {"message": "AI Finance Planner Backend is up!"}
