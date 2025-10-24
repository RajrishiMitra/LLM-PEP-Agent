from llm_agent.LLM_code import generate_pep_reports
from llm_agent.transform_schema import process_data
from llm_agent.utils import convert_datetime
import os
import json
import pandas as pd

INPUT_DIR = "data/input/CourtAppeal"
OUTPUT_FILE_PATH = "data/output/CourtAppeal_Output.json"
EXCEL_FILE_PATH = "data/input/CourtAppeal_Listing.xlsx"

if __name__ == "__main__":
    print("🚀 Starting PEP LLM Agent pipeline...")
    generate_pep_reports(EXCEL_FILE_PATH, INPUT_DIR)

    df = pd.read_excel(EXCEL_FILE_PATH)
    result = []

    for file in sorted(os.listdir(INPUT_DIR)):
        if file.endswith(".txt"):
            base_name = os.path.splitext(file)[0]
            with open(os.path.join(INPUT_DIR, file), "r", encoding="utf-8") as f:
                input_data = f.read()

            res = process_data(input_data)
            match = df[df["name"].astype(str).str.strip().eq(base_name)]
            if not match.empty:
                name = match.iloc[0]["name"]
                source_url = match.iloc[0]["link"]
                result.append({"name": name, "source_url": source_url, "data": res})
            else:
                result.append({"name": base_name, "source_url": None, "data": res})

    with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4, default=convert_datetime)

    print(f"✅ All results saved to {OUTPUT_FILE_PATH}")
