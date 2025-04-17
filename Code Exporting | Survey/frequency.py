import pandas as pd

def count_code_frequencies_detailed(input_path: str, output_path: str):
    """
    Reads the cleaned Excel file, counts frequency of each code overall
    and by each paper reference. Saves both to a new Excel file with two sheets.
    """
    # Load the cleaned data
    df = pd.read_excel(input_path)

    # === Sheet 1: Overall frequency ===
    overall_freq = df["Code"].value_counts().reset_index()
    overall_freq.columns = ["Code", "Frequency"]

    # === Sheet 2: Frequency by paper ===
    by_paper_freq = (
        df.groupby(["Ref.", "Code"])
        .size()
        .reset_index(name="Frequency")
        .sort_values(["Ref.", "Frequency"], ascending=[True, False])
    )
    
    # Reset index
    by_paper_freq = by_paper_freq.reset_index(drop=True)

    # Write to Excel with two sheets
    with pd.ExcelWriter(output_path) as writer:
        overall_freq.to_excel(writer, sheet_name="Overall Frequency", index=False)
        by_paper_freq.to_excel(writer, sheet_name="By Paper", index=False)

    print("\n🔹 Top codes overall:")
    print(overall_freq.head(10))
    print(by_paper_freq.head(10))
    print(f"\n✅ Results saved to: {output_path}")



def main():
    input_file = "/home/ciber/Desktop/I-CLAIM/Code Exporting/Literature Review - Codes.xlsx"
    output_file = "Literature Review - Frequencies.xlsx"
    count_code_frequencies_detailed(input_file, output_file)


if __name__ == "__main__":
    main()
