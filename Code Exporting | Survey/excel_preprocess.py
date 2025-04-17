import pandas as pd
import re

def clean_and_split_codes(input_path: str, output_path: str):
    """
    Reads an Excel file, splits semicolon-separated codes into separate rows,
    and writes the cleaned result to a new Excel file.
    """
    # Load the Excel file
    df = pd.read_excel(input_path)

    # Drop fully empty rows
    df = df.dropna(how="all")

    # Drop rows where 'Code' is missing
    df = df.dropna(subset=["Code"])

    # Split, strip, and remove empty codes
    df["Code"] = (
        df["Code"]
        .str.split(";")
        .apply(lambda codes: [code.strip() for code in codes if code.strip()])
    )

    # Explode the cleaned list
    df = df.explode("Code")
    
    # Clean the 'Ref.' field: keep only (Author, Year)
    def extract_author_year(ref):
        if not isinstance(ref, str):
            return None
        match = re.search(r"\(([^,]+,\s*\d{4})", ref)
        return f"({match.group(1)})" if match else None

    df["Ref."] = df["Ref."].apply(extract_author_year)
    
    # Reset index
    df = df.reset_index(drop=True)

    # Save to new Excel file
    df.to_excel(output_path, index=False)
    
    print(f"✅ Cleaned data saved to: {output_path}")
    print(df.head(10))



def main():
    input_file = "/home/ciber/Desktop/I-CLAIM/Code Exporting/Literature Review - Original Codes.xlsx"
    output_file = "Literature Review - Codes.xlsx"
    clean_and_split_codes(input_file, output_file)


if __name__ == "__main__":
    main()
