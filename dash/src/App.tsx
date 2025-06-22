import React from "react";
import BudgetDashboard from "./components/BudgetDashboard";
import TaxSummary from "./components/TaxSummary";

function App() {
  return (
    <div>
      <h1 style={{ textAlign: "center", margin: "20px 0" }}>AI Finance Planner</h1>

      <BudgetDashboard />
      <TaxSummary />
    </div>
  );
}

export default App;
