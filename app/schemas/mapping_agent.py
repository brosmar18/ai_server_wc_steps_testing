"""
Pydantic schemas for AI mapping agent output. 
These models define the structure that the AI agent must return when mapping CSV columns to CDATA fields. 
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class Mapping(BaseModel):
    """
    A single column-to-field mapping
    Represents the AI's decision about which CDATA field a 
    CSV column should map to.
    """
    column: str = Field(
        ...,
        description="The CSV column name"
    )
    fieldName: str = Field(
        ...,
        description="The CDATA field name to map to."
    )
    fieldType: str = Field(
        ...,
        description="The field type (string, number, reference, etc.)"
    )
    refObjectName: Optional[str] = Field(
        None,
        description="For reference fields, the referenced object name"
    )

class MappingObject(BaseModel):
    """
    Collection of mappings from the AI agent. 
    This is the top-level structure that the AI agent returns. 
    """
    mappings: List[Mapping] = Field(
        ...,
        description="List of column-to-field mappings"
    )