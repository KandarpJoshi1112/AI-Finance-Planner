from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents.budgeting_agent import BudgetingAgent
from agents.tax_optimizer import TaxOptimizerAgent
from agents.rebalancer_agent import build_and_train
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

@app.get("/rebalancer-summary")
def rebalancer_summary(
    tickers: str = Query(..., description="Comma-separated tickers"),
    start: str = Query("2020-01-01", description="YYYY-MM-DD"),
    end: str | None = Query(None, description="YYYY-MM-DD or nothing"),
    episodes: int = Query(500, ge=1, description="Q-learning episodes"),
):
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
        summary = build_and_train(
            tickers=ticker_list,
            start=start,
            end=end,
            episodes=episodes
        )
        return summary
    except Exception as e:
        # This will return the Python error message to your client
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")

@app.get("/")
def root():
    return {"message": "AI Finance Planner Backend is up!"}
