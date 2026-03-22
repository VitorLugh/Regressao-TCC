import pandas as pd
import os

files = [
    'Anexo-Boletim-FI-201912.xlsx',
    'Anexo-Boletim-FI-202112.xlsx',
    'Anexo_boletim_fundos_investimento_dezembro_Valor.xlsx'
]

base_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.abspath(os.path.join(base_path, '..', 'data'))

for file in files:
    full_path = os.path.join(data_path, file)
    print(f"\n{'='*20} Inspecting {file} {'='*20}")
    try:
        xl = pd.ExcelFile(full_path)
        for sheet in xl.sheet_names:
            if 'PL' in sheet or 'Patrim' in sheet:
                df = pd.read_excel(full_path, sheet_name=sheet)
                print(f"\nSheet: {sheet} (Shape: {df.shape})")
                # Look for 'Renda Fixa' in the dataframe
                rf_rows = df.apply(lambda row: row.astype(str).str.contains('Renda Fixa', case=False).any(), axis=1)
                if rf_rows.any():
                    print("Found 'Renda Fixa' in this sheet. Displaying relevant area:")
                    print(df[rf_rows].head(10))
                    # Also print the first few columns to see if they are dates
                    print("\nFirst columns and head:")
                    print(df.iloc[:10, :10])
                else:
                    print("No 'Renda Fixa' found in this sheet.")
    except Exception as e:
        print(f"Error reading {file}: {e}")
