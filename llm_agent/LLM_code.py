import os
import asyncio
import time
import random
import pandas as pd
from gpt_researcher import GPTResearcher
from llm_agent.utils import write_md_to_txt
from dotenv import load_dotenv

# Load .env
load_dotenv("config/settings.env")

os.environ["LLM_TEMPERATURE"] = os.getenv("LLM_TEMPERATURE", "0.1")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY", "")

async def get_report(query: str, report_type: str, report_format: str):
    researcher = GPTResearcher(query, report_type, report_format=report_format)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return (
        report,
        researcher.get_research_context(),
        researcher.get_costs(),
        researcher.get_research_images(),
        researcher.get_research_sources(),
        researcher,
    )

def read_excel_and_format(file_path, sheet_name=0):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df[['name', 'link']].dropna().to_dict(orient='records')

def generate_pep_reports(input_excel, output_dir):
    data = read_excel_and_format(input_excel)
    print(f"[INFO] Loaded {len(data)} entries.")

    for entry in data:
        name, url = ele['name'], ele['link']#, ele['desg']
        # url = url+"?fancybox=true"
        query = f"""
                Conduct an in-depth search across the internet to extract **complete** details about the individual listed below.
                Ensure that no attribute is left empty. Use multiple sources, prioritizing official/government websites.

                **Personal Details**:
                - Full Name, Aliases
                - Date of Birth (DD-MM-YYYY), Place of Birth, Date of Death (if applicable)
                - Gender

                **Contact Information**:
                - Emails, Phone Numbers (Mobile, Fax, Office)
                - Addresses (Residential, Official)

                **Professional Details**:
                - Current & Past Designations (with Organization & Dates: DD-MM-YYYY)
                - Include designations with start and end dates in the format DD-MM-YYYY (if available)

                **Family Members**:
                - Names & Relationships (Parents, Spouse, Children, etc.)

                **Media & References**:
                - Image URLs
                - Sources (Official/Government sites preferred)

                **Research Instructions**:
                - Search widely across the internet to ensure all requested details are obtained.
                - Cross-verify data from multiple sources to improve accuracy.
                - Ensure no field remains empty—if a value is truly unavailable, indicate "Not Found."

                **Name** : {name}
                **Reference Link**: {url}
                """
        report_type, format = "research_report", "markdown"
        report, context, costs, images, sources, researcher = asyncio.run(get_report(query, report_type, format))
        write_md_to_txt(report, name, output_dir)
        print(f"✅ Generated: {name}")
        time.sleep(random.uniform(2, 5))
