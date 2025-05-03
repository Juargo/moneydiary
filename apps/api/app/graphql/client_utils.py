import json
import re
from fastapi import Request, Response
from typing import Callable, Dict, Any
import logging

from .debug import debug_query, debug_result

# Configure detailed logging
logger = logging.getLogger(__name__)

class SnakeCaseGraphQLMiddleware:
    """
    Middleware for FastAPI that transforms GraphQL requests
    to handle snake_case to camelCase conversion automatically.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        # Check if it's a GraphQL POST request
        if scope["path"].endswith("/graphql") and scope["method"] == "POST":
            request = Request(scope=scope, receive=receive)
            
            try:
                # Get the original request body
                body_bytes = await request.body()
                original_body = body_bytes.decode('utf-8')
                
                try:
                    # Parse the body as JSON
                    data = json.loads(original_body)
                    
                    if 'query' in data:
                        # Log the original query for debugging
                        logger.debug(f"Original GraphQL query: {data['query']}")
                        
                        # Process the query to convert field names
                        query = data['query']
                        
                        # Simple field replacements for known problematic fields
                        field_replacements = {
                            'profile_image': 'profileImage',
                            'is_active': 'isActive',
                            'email_verified': 'emailVerified'
                        }
                        
                        # Replace all fields using regex pattern for field names
                        pattern = r'(\s+)([a-z][a-z0-9_]*)(\s*[{:,)])'
                        
                        def replace_field(match):
                            spaces = match.group(1)
                            field = match.group(2)
                            suffix = match.group(3)
                            
                            # Replace with camelCase if it's in our replacements dict
                            if field in field_replacements:
                                return spaces + field_replacements[field] + suffix
                            return match.group(0)
                        
                        modified_query = re.sub(pattern, replace_field, query)
                        
                        # Update query in data
                        data['query'] = modified_query
                        logger.debug(f"Modified GraphQL query: {modified_query}")
                        
                        # Create a new body with the modified query
                        modified_body = json.dumps(data).encode('utf-8')
                        
                        # Custom receive function that returns the modified body
                        async def custom_receive():
                            message = await receive()
                            if message["type"] == "http.request":
                                message["body"] = modified_body
                                message["more_body"] = False
                            return message
                        
                        # Call the app with the modified receive
                        return await self.app(scope, custom_receive, send)
                    
                except json.JSONDecodeError:
                    # Not a valid JSON, just continue
                    pass
                    
            except Exception as e:
                logger.exception(f"Error processing GraphQL query: {e}")
                
        # Default case: just pass through
        return await self.app(scope, receive, send)
