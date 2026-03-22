import pandas as pd
import os

base_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.abspath(os.path.join(base_path, '..', 'data'))
file_2022 = 'Anexo_boletim_fundos_investimento_dezembro_Valor.xlsx'
full_path = os.path.join(data_path, file_2022)

xl = pd.ExcelFile(full_path)
print(f"Sheets: {xl.sheet_names}")

# Let's try 'Pág. 3 - PL por Classe' or similar
for sheet in xl.sheet_names:
    if 'PL' in sheet:
        print(f"\n--- Checking sheet: {sheet} ---")
        df = pd.read_excel(full_path, sheet_name=sheet)
        
        # Look for "Renda Fixa" in the first few columns
        rf_rows = df.iloc[:, 0].astype(str).str.contains('Renda Fixa', case=False)
        if rf_rows.any():
            print("Found Renda Fixa row(s):")
            print(df[rf_rows])
            
            # The columns might be the dates. Let's see the headers.
            print("\nColumns:")
            print(df.columns.tolist())
            
            # If the dates are in a row, find that row
            period_rows = df.apply(lambda row: row.astype(str).str.contains('Período', case=False).any(), axis=1)
            if period_rows.any():
                print("\nPeriod row found:")
                print(df[period_rows])
        
        # Another possibility: Rows are dates, columns are classes
        date_col = None
        for col in df.columns:
            if 'Período' in str(col) or 'Data' in str(col):
                date_col = col
                break
        
        if date_col:
            print(f"Found date column: {date_col}")
            if 'Renda Fixa' in df.columns:
                print("Found Renda Fixa column. First 5 rows:")
                print(df[[date_col, 'Renda Fixa']].head())
            else:
                # Look for Renda Fixa in all headers
                rf_cols = [c for c in df.columns if 'Renda Fixa' in str(c)]
                if rf_cols:
                    print(f"Found Renda Fixa related columns: {rf_cols}")
                    print(df[[date_col] + rf_cols].head())
