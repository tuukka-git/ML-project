import pandas as pd
import sqlite3
import snowballstemmer
import re

stemmer = snowballstemmer.stemmer('finnish')

DATABASE_NAME = "kululajit.db"
TABLE_NAME = "selitetekstit"
TRAINING_DATA_DIR = "training_data"
CSV_FILES = [
    "ammattikirjallisuus.csv",
    "edustuskulut.csv",
    "henkilokunnan_koulutus.csv",
    "it-kulut.csv",
    "matkakulut.csv",
    "polttoainekulut.csv",
    "postikulut.csv",
    "toimistotarvikkeet.csv"
            ]

def preprocess(text):
    text = text.lower()
    text.replace('ä', 'ae').replace('ö', 'oe')
    text = re.sub(r'[^a-zäöå\s]', '', text)
    return text


conn = sqlite3.connect(DATABASE_NAME)
for file in CSV_FILES:
    file_path = f"{TRAINING_DATA_DIR}/{file}"
    print(file_path)
    data = pd.read_csv(file_path)
    if 'seliteteksti' in data.columns:
         data['seliteteksti'] = data['seliteteksti'].apply(preprocess)
    else:
        print("Column 'selite' not found in the data.")
        exit()
    data.to_sql('seliteteksti', conn, if_exists='append', index=False)
conn.close()

print(f"Data has been processed and saved to {DATABASE_NAME}")
