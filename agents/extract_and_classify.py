import pdfplumber
import pandas as pd
from datetime import datetime
import re

# Keyword-based categorization rules
CATEGORY_RULES = {
    "swiggy": "Food",
    "zomato": "Food",
    "blinkit": "Food",
    "petrol": "Fuel",
    "vikram petroleum": "Fuel",
    "petroleum": "Fuel",
    "hp auto": "Fuel",
    "food": "Food",
    "super market": "Grocery",
    "ixigo": "Travel",
    "bus": "Travel",
    "train": "Travel",
    "fuels": "Fuel",
    "hp": "Fuel",
    "bookmyshow": "Entertainment",
    "amazon": "Shopping",
    "meesho": "Shopping",
    "namrata": "Income",
    "mehul joshi": "Income",
    "google pay": "Income",
    "salary": "Income",
    "gtu": "Education",
    "university": "Education"
}

def categorize(description: str) -> str:
    desc = description.lower()
    for keyword, category in CATEGORY_RULES.items():
        if re.search(r'\b' + re.escape(keyword) + r'\b', desc):
            return category
    return "Other"

def extract_transactions_from_pdf(pdf_path: str) -> pd.DataFrame:
    rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                # normalize header
                header = [cell.strip().lower() if cell else "" for cell in table[0]]

                # Case A: Bank‐style with separate Debit & Credit columns
                if "debit" in header and "credit" in header and "narration" in header:
                    idx_date   = header.index("trn. date")
                    idx_narr   = header.index("narration")
                    idx_debit  = header.index("debit")
                    idx_credit = header.index("credit")

                    for row in table[1:]:
                        raw_date = row[idx_date].strip()
                        try:
                            date = datetime.strptime(raw_date, "%d-%m-%Y")
                        except:
                            continue

                        narr  = (row[idx_narr] or "").strip()
                        debit = (row[idx_debit] or "").replace(",", "").strip()
                        credit= (row[idx_credit] or "").replace(",", "").strip()

                        if debit and debit not in ("0",""):
                            amt   = float(debit)
                            ttype = "Debit"
                        elif credit and credit not in ("0",""):
                            amt   = float(credit)
                            ttype = "Credit"
                        else:
                            continue

                        rows.append({
                            "Date": date,
                            "Description": narr,
                            "Amount": amt,
                            "Type": ttype,
                            "Category": categorize(narr)
                        })

                # Case B: Paytm‐style single “Amount” column with +/- sign
                elif "amount" in header and ("transaction details" in header or "narration" in header):
                    idx_date    = header.index(next(h for h in header if "date" in h))
                    idx_narr    = header.index("transaction details") if "transaction details" in header else header.index("narration")
                    idx_amount  = header.index("amount")

                    for row in table[1:]:
                        raw_date = row[idx_date].strip()
                        # Try multiple date formats
                        for fmt in ("%d %b'%y %I:%M %p", "%d-%m-%Y", "%d %b %Y"):
                            try:
                                date = datetime.strptime(raw_date, fmt)
                                break
                            except:
                                continue
                        else:
                            continue

                        narr = (row[idx_narr] or "").strip()
                        raw_amt = (row[idx_amount] or "").replace(",", "").strip()
                        # Expect something like "+ Rs.183" or "- Rs.1,608"
                        m = re.search(r"([+-])\s*Rs\.?\s*([\d\.]+)", raw_amt)
                        if not m:
                            continue
                        sign, num = m.groups()
                        amt = float(num)
                        ttype = "Credit" if sign=="+" else "Debit"

                        rows.append({
                            "Date": date,
                            "Description": narr,
                            "Amount": amt,
                            "Type": ttype,
                            "Category": categorize(narr)
                        })

    # Always return a DataFrame with the right columns
    if not rows:
        return pd.DataFrame(columns=["Date","Description","Amount","Type","Category"])

    df = pd.DataFrame(rows)
    df.sort_values("Date", inplace=True)
    return df

def run_extraction():
    bank_pdf = "data/RCC-BANK-Statement-25.pdf"
    upi_pdf  = "data/Paytm_UPI_Statement_01_Apr'24_-_31_Mar'25.pdf"

    df_bank = extract_transactions_from_pdf(bank_pdf)
    df_upi  = extract_transactions_from_pdf(upi_pdf)

    combined = pd.concat([df_bank, df_upi], ignore_index=True)
    combined.to_csv("data/structured_transactions.csv", index=False)
    print(f"✅ Extracted {len(combined)} transactions to data/structured_transactions.csv")

if __name__ == "__main__":
    run_extraction()
