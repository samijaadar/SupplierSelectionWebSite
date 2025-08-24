import openai
import json
import re
from openai import OpenAI

openai.api_key = "sk-b0b211a091df40c0acac8b9bfba45720"
openai.base_url = "https://api.deepseek.com"
perturbation_data = None
openai.api_key = "sk-b0b211a091df40c0acac8b9bfba45720"
openai.base_url = "https://api.deepseek.com"

client = OpenAI(api_key="sk-b0b211a091df40c0acac8b9bfba45720", base_url="https://api.deepseek.com")
def scenario_generator_agent(data, columns):
    prompt = f"""
        You are a geopolitical risk analyst AI specializing in early warning systems. Based on the following real-time event feed, assess the regional stability impact. Identify key actors, historical context, and probability of escalation.

Given the following supplier attributes: {columns} and aggregated risks: {data}, generate a disruption scenario in JSON format with percentage adjustments to given attributes

Format each event like this:
- Event: [short title]
- Date: [yyyy-mm-dd]
- Location: [city, country]
- Description: [1–2 sentence impact summary]

Given the following event and supplier context, simulate the likely business impact across key KPIs.

Return only valid JSON with the following structure:

  "scenario_name": "[Location]",
  "description": "[Short explanation of how the event impacts the supplier]",
  "adjustments": 
    "Attribut_1": "[% change]",
    "Attribut_2": "[% change]",
    ....


    """


    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": "You are a helpful assistant"},
                  {"role": "user", "content": prompt}],
        stream=False
    )

    resp = response.choices[0].message.content

    print(resp)

def events_detector_agent(data):
    prompt = f"""
    You are a geopolitical risk analyst AI specializing in early warning systems. Based on the following real-time event feed, assess the regional stability impact. Identify for teh evet that can affect supply chain supplier to achieve there work the following information  key actors, historical context, and probability of escalation.


    return the result as json document with list of events and Format each event like this:
    - Event: [short title]
    - Date: [yyyy-mm-dd]
    - Location: [city, country]
    - Description: [1–2 sentence impact summary]

    Event Feed:
    {data}
    
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": "You are a helpful assistant"},
                  {"role": "user", "content": prompt}],
        stream=False
    )

    resp = response.choices[0].message.content

    print(resp)

def generate_perturbation(columns):

    prompt = f"""I have a dataset with the following columns: {columns}. I want you to generate realistic perturbations for this dataset. The perturbation should reflect a plausible real-world scenario where a value for one or more of these columns changes. For example, if "Qualité" (a quality score) drops to zero, this could mean the supplier's product quality has drastically worsened. Similarly, if "Cost" increases significantly, this might indicate price hikes due to changes in the market or supply chain issues.
    
     Please create a JSON objects that will be generic for all suppliers, representing a perturbation. The keys in the JSON objects will be the column names, and the values will be the perturbed values. Think about realistic situations where these values could change, and make sure the resulting changes reflect realistic business scenarios to test resilience.
    
     all weights should be positive and scaled
     
     weight should be between 0 and 1
    
     only one scenario
    
     exemple of result:
     {{
       "Qualité": 0.2,
       "Cost": 0.5
     }}
     """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt}],
        stream=False
    )

    resp = response.choices[0].message.content

    match = re.search(r'\{.*}', resp, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            perturbation_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
    else:
        print("No JSON found")

    return resp, perturbation_data
