"""
CDATA API operations for fetching object schemas.
Module handles: 
- Fetching object field definitions from CDATA
- HTTP communication with CDATA API
- Error handling for API Failures
"""
import httpx
from typing import List, Dict, Any
from app.core.config import config
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class CDataAPIError(Exception):
    """Raised when CDATA API calls fail"""
    pass

def fetch_object_data(object_name: str) -> List[Dict[str, Any]]:
    """
   Fetch field defs for a given object from CDATA API.
   This calls the advancedFilter/SimpleFilters endpoint which returns data about all fields in an object (field names, types, labels, etc.)
    """
    try:
        # Validate input
        if not object_name or not object_name.strip():
            raise ValueError("object_name cannot be empty")
        
        object_name = object_name.strip()

        # Build URL
        url = f"{config.CDATA_API_BASE}/rest/web/advancedFilter/simpleFilters"
        params = {"object": object_name}

        logger.info(f"Fetching object data for: {object_name}")
        logger.debug(f"URL: {url}")
        logger.debug(f"Params: {params}")


        # Make API request
        response = httpx.get(
            url=url,
            params=params,
            auth=config.CDATA_AUTH,
            timeout=30.0
        )

        # Check for HTTP errors
        response.raise_for_status()

        # Parse JSON response
        data = response.json()
        logger.info(f"Successfully fetched {len(data)} fields for object: {object_name}")
        logger.debug(f"First field (if any): {data[0] if data else 'No Fields'}")

        return data
    
    except ValueError as e:
        # Re-raise validation errors
        logger.error(f"Validation error: {e}")
        raise

    except httpx.HTTPStatusError as e:
        error_msg = f"CDATA API returned error for object '{object_name}': {e.response.status_code}"
        logger.error(error_msg)
        logger.error(f"Response body: {e.response.text}")
        raise CDataAPIError(error_msg) from e
    
    except httpx.RequestError as e:
        # Network error (connection, timeout, etc.)
        error_msg = f"Failed to connect to CDATA API for object '{object_name}': {str(e)}"
        logger.error(error_msg)
        raise CDataAPIError(error_msg) from e
        
    except Exception as e:
        # Unexpected error
        error_msg = f"Unexpected error fetching object data for '{object_name}': {str(e)}"
        logger.error(error_msg)
        raise CDataAPIError(error_msg) from e