import re
from typing import Dict, Any, List, Union

def snake_to_camel_case(snake_str: str) -> str:
    """
    Convert a snake_case string to camelCase
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def camel_to_snake_case(camel_str: str) -> str:
    """
    Convert a camelCase string to snake_case
    """
    result = [camel_str[0].lower()]
    for char in camel_str[1:]:
        if char.isupper():
            result.append('_')
            result.append(char.lower())
        else:
            result.append(char)
    return ''.join(result)

def transform_query_fields(query: str) -> str:
    """
    Transform a GraphQL query by replacing snake_case field names with camelCase ones
    
    This is particularly useful for client code that uses snake_case conventions
    but needs to interact with a GraphQL API using camelCase.
    """
    # Regular expression to find field names in a GraphQL query
    # This is a simplified version and might need adjustments for complex queries
    field_pattern = r'(?<=\s)([a-z][a-z0-9_]*)(?=\s*[{\s,)]|$)'
    
    def replace_field(match):
        field_name = match.group(0)
        if '_' in field_name:
            return snake_to_camel_case(field_name)
        return field_name
    
    transformed_query = re.sub(field_pattern, replace_field, query)
    return transformed_query

def transform_variables(variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform variable names in a GraphQL variables dictionary from snake_case to camelCase
    """
    if not variables:
        return {}
        
    transformed = {}
    for key, value in variables.items():
        camel_key = snake_to_camel_case(key)
        
        # Handle nested dictionaries and lists
        if isinstance(value, dict):
            transformed[camel_key] = transform_variables(value)
        elif isinstance(value, list):
            transformed[camel_key] = [
                transform_variables(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            transformed[camel_key] = value
            
    return transformed

def transform_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform field names in a GraphQL result from camelCase to snake_case
    """
    return _transform_dict_keys(result, camel_to_snake_case)

def _transform_dict_keys(obj: Any, transform_func: callable) -> Any:
    """
    Recursively transform all dictionary keys in an object
    using the provided transform function
    """
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            new_key = transform_func(key) if isinstance(key, str) else key
            new_dict[new_key] = _transform_dict_keys(value, transform_func)
        return new_dict
    elif isinstance(obj, list):
        return [_transform_dict_keys(item, transform_func) for item in obj]
    else:
        return obj
