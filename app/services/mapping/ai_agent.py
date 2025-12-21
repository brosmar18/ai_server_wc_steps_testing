"""
AI mapping agent creation and configuration. 
This module handles creating the OpenAI agent that maps
CSV columns to CDATA fields.
"""
import json
import os
from typing import List, Dict
from agents import Agent
from app.schemas.mapping_agent import MappingObject
from app.core.config import config
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def create_mapping_agent() -> Agent:
    """
    Function to create AI mapping agent.
    The agent is configured with specific instructions on how to map
    CSV column names to CDATA field names by analyzing: 
    - Field name (The name of the field in the database.)
    - Field label (Human-readable name)
    - Field type (string, reference, etc)
    - Whats This (Help text)
    """
    try:
        logger.info("Creating AI mapping agent")

        os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
        logger.debug("OpenAI API key set in .env")

        agent = Agent(
            name="mapping_agent",
            instructions="""
                You are an expert at mapping CSV column names to database field definitions.

                The user will provide:
                1) A list of column names from a CSV file
                2) A fields object containing field definitions

                Your job is to map each column to its corresponding fieldName using the fieldName, 
                field label, fieldType, and whats_this (help text) values to support your reasoning.

                You will also note the fieldType value for the field that you mapped to a column.
                If the field is a reference field, you should include the refObjectName when provided.

                Example Input:
                - Column list: ["Employee Number", "First Name", "Last Name"]
                - Fields object:
                {
                    "fields": [
                    {
                        "fieldName": "empno",
                        "label": "Emp No",
                        "fieldType": "string",
                        "whats_this": "Employee Number"
                    },
                    {
                        "fieldName": "lname",
                        "label": "Last Name",
                        "fieldType": "string",
                        "whats_this": "Enter the employee's last name"
                    },
                    {
                        "fieldName": "fname",
                        "label": "First Name",
                        "fieldType": "string",
                        "whats_this": "Enter the employee's first name"
                    },
                    {
                        "fieldName": "emptitle",
                        "label": "Primary Job Title",
                        "fieldType": "reference",
                        "whats_this": "Select the Job Title for this employee.",
                        "refObjectName": "emptitle"
                    }
                    ]
                }

                Example Output:
                You would map:
                - "Employee Number" → fieldName "empno"
                - "First Name"      → fieldName "fname"
                - "Last Name"       → fieldName "lname"

                CRITICAL: Return ONLY valid JSON with this exact structure:

                {
                "mappings": [
                    {
                    "column": "<column name from the CSV>",
                    "fieldName": "<matching fieldName from the fields object>",
                    "fieldType": "<fieldType from the matching field>",
                    "refObjectName": "<refObjectName when fieldType == 'reference', otherwise omit this key>"
                    }
                ]
                }

                Rules:
                - Do not include any extra keys or explanation text
                - The JSON must match this structure exactly
                - For reference fields, include refObjectName
                - For non-reference fields, omit refObjectName (do not include it as null)
                - Map ALL columns provided
                - Use exact field names from the fields object
            """,
            output_type=MappingObject,
        )
        logger.info("AI mapping agent created successfully!")
        return agent
    
    except Exception as e:
        logger.error(f"Failed to create mapping agent: {e}")
        raise


def build_prompt(columns: List[str], fields: List[Dict]) -> str:
    """
    Build the prompt for the AI agent. 
    Formates the columsna and fields into a prompt that the agent can understand. 
    """
    try:
        payload = {"fields": fields}
        fields_json = json.dumps(payload, ensure_ascii=False)

        prompt = f"Column List: {columns},\nFields Object: {fields_json}"

        logger.debug(f"Built prompt with {len(columns)} columns and {len(fields)} fields")

        return prompt 
    
    except Exception as e:
        logger.error(f"Failed to build prompt: {e}")
        raise