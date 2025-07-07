from __future__ import annotations
import logging
from typing import Any, Dict, Optional

# Configure detailed logging
logger = logging.getLogger("graphql.debug")
logger.setLevel(logging.DEBUG)

def debug_query(query: str, variables: Optional[Dict] = None):
    """
    Log a GraphQL query for debugging purposes
    """
    logger.debug(f"GraphQL Query:")
    logger.debug(f"{query}")
    if variables:
        logger.debug(f"Variables: {variables}")

def debug_result(result: Any):
    """
    Log a GraphQL query result for debugging
    """
    logger.debug(f"GraphQL Result: {result}")
