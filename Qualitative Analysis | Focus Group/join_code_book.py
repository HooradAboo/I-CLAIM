'''
    This code get the code "Frequencies" sheet (ouput from mrege_frequencies)'''

import pandas as pd


definition_adr = "./Code Book(Dictionary).csv"
frequency_adr = "./Code Book(Frequencies).csv"

definition = pd.read_csv(definition_adr)
frequency = pd.read_csv(frequency_adr)

merged = pd.merge(frequency, definition, how='outer', on=["Code"])

merged = merged[['Code', 'Description', 'Hoorad', 'Anam', 'Joshua']]

merged.to_csv('Joined Code Book.csv')