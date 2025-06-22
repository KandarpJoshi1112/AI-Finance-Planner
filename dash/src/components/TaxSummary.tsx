import React, { useEffect, useState } from "react";
import axios from "axios";

type OldTax = {
  regime: "old";
  gross_income: number;
  standard_deduction: number;
  used_80C: number;
  remaining_80C: number;
  limit_80C: number;
  taxable_income: number;
  tax_before_cess: number;
  tax_with_cess: number;
  rebate_threshold: number;
  rebate_limit: number;
  rebate_applied: number;
  remaining_for_rebate: number;
  tax_after_rebate: number;
};

type NewTax = {
  regime: "new";
  gross_income: number;
  standard_deduction: number;
  used_80C: number; // always 0
  remaining_80C: number; // always 0
  limit_80C: number; // always 0
  taxable_income: number;
  tax_before_rebate: number;
  rebate_threshold: number;
  rebate_limit: number;
  rebate_applied: number;
  remaining_for_rebate: number;
  tax_after_rebate: number;
};

type TaxResponse = { tax: OldTax | NewTax };

const TaxSummary: React.FC = () => {
  const [regime, setRegime] = useState<"old" | "new">("old");
  const [tax, setTax] = useState<OldTax | NewTax | null>(null);

  useEffect(() => {
    axios
      .get<TaxResponse>(`http://localhost:8000/tax-summary?regime=${regime}`)
      .then((res) => setTax(res.data.tax))
      .catch(console.error);
  }, [regime]);

  if (!tax) return <div>Loading tax data…</div>;

  return (
    <div style={{ padding: 20, background: "#eef", borderRadius: 8, marginTop: 40 }}>
      <h2>Tax Summary</h2>

      <label>
        <strong>Regime:</strong>{" "}
        <select value={regime} onChange={(e) => setRegime(e.target.value as any)}>
          <option value="old">Old (with 80C & ₹12.5k rebate)</option>
          <option value="new">New (no 80C & ₹60k rebate)</option>
        </select>
      </label>

      <div style={{ marginTop: 20 }}>
        <p>
          <strong>Gross Income:</strong> ₹{tax.gross_income.toLocaleString()}
        </p>
        <p>
          <strong>Standard Deduction:</strong> ₹{tax.standard_deduction.toLocaleString()}
        </p>

        {tax.regime === "old" && (
          <>
            <h3>80C Investments</h3>
            <p>
              Used: ₹{tax.used_80C.toLocaleString()} of ₹{tax.limit_80C.toLocaleString()}
            </p>
            {tax.remaining_80C > 0 && (
              <p style={{ color: "#b33" }}>
                Invest ₹{tax.remaining_80C.toLocaleString()} more to fully use 80C.
              </p>
            )}
          </>
        )}

        <h3>Rebate (Section 87A)</h3>
        <p>Threshold: ₹{tax.rebate_threshold.toLocaleString()}</p>
        <p>Applied: ₹{tax.rebate_applied.toLocaleString()}</p>
        {tax.remaining_for_rebate > 0 ? (
          <p style={{ color: "#b33" }}>
            You are ₹{tax.remaining_for_rebate.toLocaleString()} away from rebate threshold.
          </p>
        ) : (
          <p style={{ color: "#3a3" }}>You qualify for full rebate!</p>
        )}

        <h3>Tax Computation</h3>
        {tax.regime === "old" ? (
          <p>
            Tax before cess: ₹{(tax as OldTax).tax_before_cess.toLocaleString()}
            <br />
            Tax after cess: ₹{(tax as OldTax).tax_with_cess.toLocaleString()}
          </p>
        ) : (
          <p>Tax before rebate: ₹{(tax as NewTax).tax_before_rebate.toLocaleString()}</p>
        )}
        <p>
          <strong>Net Tax Payable (incl. cess):</strong> ₹{tax.tax_after_rebate.toLocaleString()}
        </p>
      </div>
    </div>
  );
};

export default TaxSummary;
