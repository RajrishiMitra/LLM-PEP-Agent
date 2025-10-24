import openai
import os
import numpy as np
from datetime import datetime
import json
import pandas as pd
from dotenv import load_dotenv
def convert_datetime(obj):
    """Custom JSON serializer for non-standard types."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, np.integer):  # Handle NumPy int64 and similar types
        return int(obj)
    elif isinstance(obj, np.floating):  # Handle NumPy float64 and similar types
        return float(obj)
    elif isinstance(obj, np.ndarray):  # Handle NumPy arrays
        return obj.tolist()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
def base_data_extraction_prompt(source_data):
    prompt = f""" 
        You are a PEP (Politically Exposed Person) agent. Your task is to analyze the unstructured content delimited by `` and extract the relevant data of the individual mentioned. Follow these instructions:
         `{source_data}`

        - **name** (string): The full legal name of the individual.
        - **aliases** (array of strings): Any nicknames, alternative names in different languages, or pseudonyms.
        - **gender** (string): The gender of the individual.
        - **dob** (string, format: "YYYY-MM-DD"): Date of birth.
        - **pob** (string): Place of birth.
        - **other_details** (string): Concise additional biographical information (e.g., "U.S. Representative, veteran, entrepreneur").
        - **phone_numbers** (array of strings): All phone numbers, formatted in the proper international format.
        - **emails** (array of strings): A list of valid email addresses.
        - **websites** (array of strings): All associated websites.
        - **digital_wallets** (array of strings): Any digital wallet addresses.
        - **social_media_handles** (array of strings): All social media profiles or handles.
        - **addresses** (array of objects): For each address, provide:
            - **complete_address** (string): The full address.
            - **city** (string): The city of residence.
            - **state** (string): The state or region of residence.
            - **country** (string): The country of residence.
            - **zip_code** (string): The postal or zip code.
        - **designation_list** (array of objects): For every position, title, or role held by the individual (e.g., "Mayor," "Councilor," "U.S. Representative"), include:
            - **designation** (string): The specific position or title.
            - **start_date** (string, format: "YYYY-MM-DD"): The start date of the role.
            - **end_date** (string, format: "YYYY-MM-DD"): The end date of the role (if applicable).
        - **relationship_details** (array of objects): Capture all relationships with other individuals. Each object should include:
            - **family_members** (array of objects): Each with the family member's name and their relationship to the individual.
            - **associates** (array of objects): Each with the associate's name and their relationship to the individual.
        - **URL_list** (array of strings): A list of URLs visited during the information-gathering process.

        Ensure that the extracted information adheres strictly to the specified data types and formats, and that it accurately reflects the content provided.
    """
    return prompt

def strict_rules_prompt(source_data):
    prompt = f""" 
        You are a PEP (Politically Exposed Person) agent. Your task is to analyze the extracted content enclosed within `` and extract structured data of the mentioned individual.  
        Follow these strict rules to ensure accuracy and consistency:
        
        `{source_data}`

        - **name**: Must not contain special characters, numbers, or prefixes (e.g., Mr., Mrs., Dr.).
        - **aliases**: Should include all known nicknames, alternative names in different languages, or pseudonyms.
        - **gender**: Must be one of the following: "Male", "Female", or "Other".
        - **dob (Date of Birth)**: Must follow the format `YYYY-MM-DD`.
        - **pob (Place of Birth)**: Must be a valid geographical location.
        - **other_details**: Must be a concise summary of additional biographical information.
        - **phone_numbers**: Must be in proper international format (e.g., `+1-123-456-7890`).
        - **emails**: Must be valid email addresses containing a `<local_part>`, `@` symbol, and `<domain_part>`.
        - **websites**: Must be valid URLs starting with `http://` or `https://`, optionally including `www.`, followed by a valid domain name and TLD (e.g., `.com`, `.org`).
        - **digital_wallets**: Must be valid digital wallet addresses.
        - **social_media_handles**: Must be valid social media profile links or handles.
        - **addresses**: Must contain the following structured components:
            - **complete_address**: Only the street address, excluding city, state, or country.
            - **city**: Must be a valid city name.
            - **state**: Must be a valid state or region name.
            - **country**: Must be a valid country name.
            - **zip_code**: Must be a valid postal or ZIP code.
        - **designation_list**: Must include all designations with start and end dates.
            - **designation**: Must follow the format `<designation-organization, country_official>` (e.g., "Minister of Finance - Government of India").
            - **start_date**: Must be in the format `YYYY-MM-DD`.
            - **end_date**: Must be in the format `YYYY-MM-DD`.
        - **relationship_details**: Must include family members and associates.
            - **family_members**: Each entry must include the family member's name and their relationship to the individual.
            - **associates**: Each entry must include the associate's name and their relationship to the individual.
            - **Valid relationship types**: 
              `Agent_Representative, Associate, Aunt, Brother, Brother_In_Law, Child, Colleague, Cousin, Daughter, Daughter_In_Law, Employee, Ex_Husband, Ex_Wife, Family_Member, Father, Father_In_Law, Financial_Adviser, Friend, Granddaughter, Grandfather, Grandmother, Grandson, Husband, Legal_Adviser, Mother, Mother_In_Law, Nephew, Niece, Partner, Political_Adviser, Sister, Sister_In_Law, Son, Son_In_Law, Spouse, Step_Daughter, Step_Father, Step_Mother, Step_Sister, Step_Son, Uncle, Unmarried_Partner, Wife`.
              Example response structure:
            [
                {{
                    "relationship": "spouse",
                    "name": ["Jane Doe"]
                }},
                {{
                    "relationship": "child",
                    "name": ["John Doe Jr.", "Sophie Doe"]
                }}
           ]
        - **URL_list**: Must contain a list of valid URLs accessed during the information-gathering process.
        
        RULES: 
        - Ensure strict adherence to the specified data formats and structure. Extracted information must be accurate, properly formatted, and reflect the provided content with precision.
        - Remove any placeholder values like null, not found, Not specified, NA, or not available.
        - If family members or associates are not mentioned, leave the field blank. 
            "relationship_details": {{
                "family_members": [],
                "associates": [] 
            }}
        - If any information is missing or unclear, leave the field blank or mark it as "".
    """
    return prompt

def schema_transform_prompt(source_data):
    prompt = f""" 
        You are a PEP (Politically Exposed Person) data transformation agent. Your task is to analyze the data enclosed within triple backticks (` ``` `) and structure it strictly in the JSON format below.
        **Important Instructions:**
        - **Return only valid JSON output**.
        - **Do not include explanations, comments, or extra text**.
        - **Ensure double quotes (`"`) are used for all keys and string values**.
        - **Check that brackets `{{}}` and `[]` are properly closed**.
        - **If a field has no data, return an empty list `[]` or `null`, but do not remove the field**.
        - **Escape any special characters** that may cause JSON formatting issues.

        Data Schema:
        {{
            "name": "Bhishma Raj Angdembe",
            "alias": [
                "Bhishmaraj Angdembe",
                "Bhisma Raj Angdambe",
                "भीष्मराज आङदेम्बे"
            ],
            "country": [
                "Nepal"
            ],
            "image_url": [],
            "address": [{{
                "complete_address": "Pashmul village, Panjwai District",
                "city": "Delhi",
                "state": "Delhi",
                "country": "India",
                "zip_code": "A233-908"
            }}],
            "individual_details": {{
                "gender": "",
                "date_of_birth": [],
                "place_of_birth": [],
                "date_of_deceased": "",
                "nationality": [],
                "citizenship": [],
                "designation_list": [
                    {{
                        "designation": "Deputy General Secretary of  Nepali Congress",
                        "designation_start_date": "2021-12-17",
                        "designation_end_date": null
                    }},
                    {{
                        "designation": "Member of  2nd Nepalese Constituent Assembly",
                        "designation_start_date": "2013-01-01",
                        "designation_end_date": "2017-01-01"
                    }}
                ],
                "individual_remark": ""
            }},
            "communication_details": {{
                "phone_numbers": [],
                "emails": [],
                "websites": [],
                "digital_wallets": [],
                "social_media_handles": []
            }},
            "documents": {{}},
            "relationship_details": {{
                "family_members": {{
                    {{
                        "relationship": "spouse",
                        "name": ["Jane Doe"]
                    }},
                    {{
                        "relationship": "child",
                        "name": ["John Doe Jr.", "Sophie Doe"]
                    }}
                }},
                "associates": {{}}
            }},
            "url_list": []
        }}
         Input Data:
        `{source_data}`

        **Transformation Rules:**
        - Extract all relevant information from the input while ensuring **no data loss**.
        - **Strictly adhere to the provided JSON schema** without omitting required fields.
        - Ensure all list fields (e.g., `alias`, `country`, `date_of_birth`) contain lists (`[]` if empty).
        - If a field has no value, return `null` (for single values) or `[]` (for lists).
        - **Do not add extra text** before or after the JSON output.
        - **Return only the JSON object**.

        **Output Format:**
        - Your response **must start with `{{` and end with `}}`**.
        - The JSON **must be properly formatted and parseable without errors**.
        """
    return prompt

def generate_result(prompt):
    # tik=datetime.now()
    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        # response_format_type="json_object",
        api_key=openai_key,
        temperature=0.0,
        # Pre-define conversation messages for the possible roles 
        messages=[
            {"role": "system", "content": "You are a PEP analyst. You need to analyze the unstructured content based upon the given input and return the output in given structured schema extracting all the information efficiently and accurately"},
            {"role": "user", "content": prompt}
        ]
    )

    # tok=datetime.now()
    try:
        op=completion.choices[0].message
    except Exception as ex:
        print("[OPEN AI - ERROR] : ",ex)
        op = {
            "content" : f"{ex}"
        }

    # input_token, in_cost=calculate_tokens_and_cost(prompt,model="gpt-4o-mini",price_per_token=(0.15 / 1000000))
    # output_token, out_cost=calculate_tokens_and_cost(op['content'],model="gpt-4o-mini",price_per_token=(0.6 / 1000000))

    # time=tok-tik
    return op #, time, (in_cost+out_cost), (input_token+output_token)
def process_data(input_data):
    base_output = generate_result(base_data_extraction_prompt(input_data))
    fixed_output = generate_result(strict_rules_prompt(base_output))
    final_output = generate_result(schema_transform_prompt(fixed_output))
    
    return final_output["content"]

# INPUT_DIR = r"/home/ubuntu/LLM_PEP/Malaysia/tavily_output"
# OUTPUT_FILE_PATH = r"/home/ubuntu/LLM_PEP/Malaysia/Malaysia_Results(tavily).json"

# processed_files = set()  # Track processed files
# result = []
# for file_name in sorted(os.listdir(INPUT_DIR)):  # Sort to maintain order
#     if file_name.endswith(".txt"):
#         file_path = os.path.join(INPUT_DIR, file_name)
        
#         # Check if file was already processed
#         if file_name in processed_files:
#             print(f"Skipping duplicate file: {file_name}")
#             continue

#         print(f"Processing file: {file_name}")
        
#         with open(file_path, "r", encoding="utf-8") as f:
#             input_data = f.read()

#         res = process_data(input_data)
#         print(res)
#         result.append(res)

#         # Mark file as processed
#         processed_files.add(file_name)
# try:
#     with open(OUTPUT_FILE_PATH, "w", encoding='utf-8') as outfile:
#         json.dump(result, outfile, ensure_ascii=False, indent=4, default=convert_datetime)
#     print(f"Results saved to {OUTPUT_FILE_PATH}")
# except TypeError as e:
#     print(f"Error during JSON serialization: {e}")

# INPUT_JSON_FILE = r"/home/ubuntu/LLM_PEP/3-LLM/HAWAI_PDF_Data.json"
# OUTPUT_FILE_PATH = r"/home/ubuntu/LLM_PEP/3-LLM/HAWAI_PDF_Transformed_Data 2.json"

# processed_entries = set()  # Track processed items based on unique identifier
# result = []

# # Load JSON file
# with open(INPUT_JSON_FILE, "r", encoding="utf-8") as json_file:
#     data_list = json.load(json_file)  # Expected format: List of dictionaries

# c = 0
# # Traverse each dictionary in the JSON list
# for entry in data_list:
#     unique_key = entry.get("name")  # Choose a unique identifier
    
#     if not unique_key:
#         print("Skipping entry without a unique identifier:", entry)
#         continue
    
#     # Check if entry was already processed
#     if unique_key in processed_entries:
#         print(f"Skipping duplicate entry: {unique_key}")
#         continue

#     print(f"Processing entry: {unique_key}")
    
#     input_data = entry.get("content", "")  # Extract content from dictionary
    
#     # print(input)
#     # Call the processing function
#     res = process_data(input_data)
    
#     # Append the result with the original entry's metadata
#     print(res)
#     entry["processed_result"] = res
#     result.append(entry)

#     # Mark as processed
#     processed_entries.add(unique_key)
#     # c += 1
#     # if c == 5:
    #     break

# Save results to JSON file
# with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as output_file:
#     json.dump(result, output_file, indent=4, ensure_ascii=False)

# print(f"Processing complete. Results saved to {OUTPUT_FILE_PATH}")


# Define paths
INPUT_DIR = r"/home/ubuntu/LLM_PEP/3-LLM/CourtAppeal/Output"
OUTPUT_FILE_PATH = r"/home/ubuntu/LLM_PEP/3-LLM/CourtAppeal/CourtAppeal_Output.json"
EXCEL_FILE_PATH = r"/home/ubuntu/LLM_PEP/3-LLM/CourtAppeal/CourtAppeal_Listing.xlsx"

# Load the Excel file
df = pd.read_excel(EXCEL_FILE_PATH)

processed_files = set()  # Track processed files
result = []

# Sort files to maintain order
for file_name in sorted(os.listdir(INPUT_DIR)):
    try:
        if file_name.endswith(".txt"):
            file_path = os.path.join(INPUT_DIR, file_name)
            base_name = os.path.splitext(file_name)[0]  # Remove .txt extension

            # Check if the file was already processed
            if file_name in processed_files:
                print(f"Skipping duplicate file: {file_name}")
                continue

            print(f"Processing file: {file_name}")
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    input_data = f.read()
            except Exception as e:
                print(f"Error reading file {file_name}: {e}")
                continue
            
            try:
                res = process_data(input_data)
            except Exception as e:
                print(f"Error processing data from {file_name}: {e}")
                continue
            
            try:
                # Find matching row in the Excel file
                match = df[df['name'].astype(str).str.strip().eq(base_name)]
                if not match.empty:
                    name = match.iloc[0]['name']
                    source_url = match.iloc[0]['link']
                    res = {"name": name, "source_url": source_url, "data": res}
                    print(res)
                else:
                    print(f"No matching entry found for: {file_name}")
                    res = {"name": base_name, "source_url": None, "data": res}
                    print(res)
                
                result.append(res)
            except Exception as e:
                print(f"Error finding match in Excel for {file_name}: {e}")
                continue

            # Mark file as processed
            processed_files.add(file_name)
    except Exception as e:
        print(f"Unexpected error processing {file_name}: {e}")

try:
    with open(OUTPUT_FILE_PATH, "w", encoding='utf-8') as outfile:
        json.dump(result, outfile, ensure_ascii=False, indent=4, default=convert_datetime)
    print(f"Results saved to {OUTPUT_FILE_PATH}")
except TypeError as e:
    print(f"Error during JSON serialization: {e}")