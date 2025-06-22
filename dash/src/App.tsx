import React from "react";
import BudgetDashboard from "./components/BudgetDashboard";
import TaxSummary from "./components/TaxSummary";
import RebalancerDashboard from "./components/RebalancerDashboard";
function App() {
  return (
    <div>
      <h1 style={{ textAlign: "center", margin: "20px 0" }}>AI Finance Planner</h1>

      <BudgetDashboard />
      <TaxSummary />
      <RebalancerDashboard />
    </div>
  );
}

export default App;
