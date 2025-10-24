# PEP LLM Agent

This project is an automated agent that leverages Large Language Models (LLMs) to research and compile reports on Politically Exposed Persons (PEPs). It extracts information from various sources, processes the data, and generates structured JSON output.

## Functionality

The PEP LLM Agent performs the following key functions:

- **Data Ingestion**: Reads a list of individuals from an Excel file.
- **Automated Research**: Uses the `gpt_researcher` library to conduct online research for each individual.
- **Report Generation**: Generates detailed reports in Markdown format based on the research.
- **Data Transformation**: Parses the generated reports, extracts structured data, and transforms it into a predefined JSON schema.
- **Output Generation**: Saves the final structured data as a single JSON file.

## Project Structure

```
.
├── llm_agent
│   ├── LLM_code.py
│   ├── transform_schema.py
│   └── utils.py
├── data
│   ├── input
│   │   └── CourtAppeal_Listing.xlsx
│   └── output
│       └── CourtAppeal_Output.json
├── config
│   └── settings.env
├── run_pep_agent.py
└── requirements.txt
```

### Key Files

- **`run_pep_agent.py`**: The main script to execute the entire pipeline.
- **`llm_agent/LLM_code.py`**: Contains the core logic for generating PEP reports using `gpt_researcher`.
- **`llm_agent/transform_schema.py`**: Handles the transformation of raw text into a structured JSON format.
- **`llm_agent/utils.py`**: Provides utility functions for file handling and data conversion.
- **`config/settings.env`**: Configuration file for API keys and other settings.
- **`requirements.txt`**: Lists the Python dependencies for the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Pip for package management

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Create a `config` directory if it doesn't exist:**
   ```bash
   mkdir config
   ```

2. **Create a `settings.env` file in the `config` directory and add your API keys:**
   ```
   OPENAI_API_KEY="your_openai_api_key"
   TAVILY_API_KEY="your_tavily_api_key"
   LLM_TEMPERATURE="0.1"
   ```

### Execution

1. **Prepare your input data:**
   - Place your Excel file (e.g., `CourtAppeal_Listing.xlsx`) in the `data/input/` directory. The Excel file should have `name` and `link` columns.

2. **Run the agent:**
   ```bash
   python run_pep_agent.py
   ```

3. **Find the output:**
   - The generated reports will be saved as text files in the `data/input/CourtAppeal/` directory.
   - The final structured JSON output will be saved in `data/output/CourtAppeal_Output.json`.

## Data Formats

### Input

The primary input is an Excel file (e.g., `CourtAppeal_Listing.xlsx`) located in the `data/input/` directory. The file should contain the following columns:

- **`name`**: The full name of the individual to be researched.
- **`link`**: A reference URL for the individual.

### Output

The final output is a single JSON file (e.g., `CourtAppeal_Output.json`) in the `data/output/` directory. It contains a list of objects, where each object represents an individual and has the following structure:

```json
{
    "name": "Full Name",
    "source_url": "http://example.com",
    "data": {
        "name": "Full Name",
        "alias": ["Alias1", "Alias2"],
        "country": ["Country"],
        "image_url": [],
        "address": [{
            "complete_address": "Street Address",
            "city": "City",
            "state": "State",
            "country": "Country",
            "zip_code": "Zip Code"
        }],
        "individual_details": {
            "gender": "Gender",
            "date_of_birth": ["YYYY-MM-DD"],
            "place_of_birth": ["Place of Birth"],
            "date_of_deceased": "YYYY-MM-DD",
            "nationality": [],
            "citizenship": [],
            "designation_list": [{
                "designation": "Designation",
                "designation_start_date": "YYYY-MM-DD",
                "designation_end_date": "YYYY-MM-DD"
            }],
            "individual_remark": ""
        },
        "communication_details": {
            "phone_numbers": [],
            "emails": [],
            "websites": [],
            "digital_wallets": [],
            "social_media_handles": []
        },
        "documents": {},
        "relationship_details": {
            "family_members": [{
                "relationship": "spouse",
                "name": ["Jane Doe"]
            }],
            "associates": {}
        },
        "url_list": []
    }
}
```

## Technologies Used

- **Python**: The core programming language.
- **OpenAI GPT-4**: Used for natural language processing and data extraction.
- **gpt-researcher**: A library for automated online research.
- **Pandas**: For reading and processing Excel files.
- **python-dotenv**: For managing environment variables.
