"""
JSON to TOON Converter Plugin for Dify
Converts JSON content to TOON (Token-Oriented Object Notation) format
to significantly reduce token usage in LLM interactions.
"""

import json
from typing import Any, Dict, List, Union
from flask import Flask, request, jsonify

app = Flask(__name__)


def json_to_toon(data: Any, indent: int = 0) -> str:
    """
    Convert JSON data to TOON format.
    
    TOON (Token-Oriented Object Notation) removes redundant symbols
    like braces, brackets, and quotes while maintaining structure clarity.
    
    Args:
        data: The data to convert (dict, list, or primitive)
        indent: Current indentation level
        
    Returns:
        TOON formatted string
    """
    indent_str = "  " * indent
    
    if isinstance(data, dict):
        if not data:
            return "{}"
        
        lines = []
        for key, value in data.items():
            if isinstance(value, (dict, list)) and value:
                if isinstance(value, list):
                    # Handle list of objects
                    if value and isinstance(value[0], dict):
                        # Check if all items are simple objects (no nested complex types)
                        all_simple = all(
                            isinstance(item, dict) and 
                            not any(isinstance(v, (dict, list)) for v in item.values())
                            for item in value
                        )
                        
                        if all_simple:
                            # Extract keys from first object
                            keys = list(value[0].keys())
                            lines.append(f"{indent_str}{key}[{len(value)}]{{{','.join(keys)}}}:")
                            for item in value:
                                if isinstance(item, dict):
                                    values = [str(item.get(k, "")) for k in keys]
                                    lines.append(f"{indent_str}  {','.join(values)}")
                                else:
                                    lines.append(f"{indent_str}  {item}")
                        else:
                            # Complex nested structures - use nested format
                            lines.append(f"{indent_str}{key}[{len(value)}]:")
                            for item in value:
                                item_str = json_to_toon(item, indent + 1)
                                for line in item_str.split('\n'):
                                    if line.strip():
                                        lines.append(line)
                    else:
                        # Simple list
                        lines.append(f"{indent_str}{key}[{len(value)}]:")
                        for item in value:
                            item_str = json_to_toon(item, indent + 1)
                            lines.append(f"{indent_str}  {item_str}")
                else:
                    # Nested dict
                    lines.append(f"{indent_str}{key}:")
                    nested = json_to_toon(value, indent + 1)
                    for line in nested.split('\n'):
                        if line.strip():
                            lines.append(line)
            else:
                # Primitive value
                value_str = str(value) if value is not None else "null"
                lines.append(f"{indent_str}{key}: {value_str}")
        
        return '\n'.join(lines)
    
    elif isinstance(data, list):
        if not data:
            return "[]"
        
        lines = []
        # Check if it's a list of objects
        if data and isinstance(data[0], dict):
            keys = list(data[0].keys())
            lines.append(f"{indent_str}[{len(data)}]{{{','.join(keys)}}}:")
            for item in data:
                if isinstance(item, dict):
                    values = [str(item.get(k, "")) for k in keys]
                    lines.append(f"{indent_str}  {','.join(values)}")
                else:
                    lines.append(f"{indent_str}  {json_to_toon(item, indent + 1)}")
        else:
            # Simple list
            for item in data:
                item_str = json_to_toon(item, indent)
                lines.append(f"{indent_str}{item_str}")
        
        return '\n'.join(lines)
    
    else:
        # Primitive value
        if data is None:
            return "null"
        elif isinstance(data, bool):
            return str(data).lower()
        elif isinstance(data, (int, float)):
            return str(data)
        else:
            return str(data)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/convert', methods=['POST'])
def convert():
    """
    Convert JSON content to TOON format.
    
    Request body:
        {
            "json_content": "string"  # JSON string to convert
        }
    
    Returns:
        TOON formatted string
    """
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "Request body is required"}), 400
        
        json_content = request_data.get('json_content')
        
        if json_content is None:
            return jsonify({"error": "json_content field is required"}), 400
        
        # Parse JSON string
        try:
            if isinstance(json_content, str):
                data = json.loads(json_content)
            else:
                data = json_content
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400
        
        # Convert to TOON
        toon_output = json_to_toon(data)
        
        return toon_output, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)

