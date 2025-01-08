from typing import List, Type, Optional, Dict, Any
from pydantic import BaseModel, create_model
from crewai.tools import BaseTool
from mcpx import Client
import json

class MCPTool(BaseTool):
    """Wrapper for mcp.run tools to be used with CrewAI."""
    name: str
    description: str
    _client: Client
    _tool_name: str

    def _run(self, text: Optional[str] = None, **kwargs) -> str:
        """Execute the mcp.run tool with the provided arguments."""

        try:
            if text:
                try:
                    input_dict = json.loads(text)
                except json.JSONDecodeError:
                    input_dict = {"text": text}
            else:
                input_dict = kwargs

            # Call the mcp.run tool with the input arguments
            results = self._client.call(self._tool_name, input=input_dict)
            
            output = []
            for content in results.content:
                if content.type == "text":
                    output.append(content.text)
            return "\n".join(output)
        except Exception as e:
            raise RuntimeError(f"MCPX tool execution failed: {str(e)}")

def get_mcprun_tools(session_id: Optional[str] = None) -> List[BaseTool]:
    """Create CrewAI tools from installed mcp.run tools."""
    client = Client(session_id=session_id)
    crew_tools = []

    for tool_name, tool in client.tools.items():
        # Create the Pydantic model from the schema
        args_schema = _convert_json_schema_to_pydantic(
            tool.input_schema,
            f"{tool_name}Schema"
        )

        # Create the CrewAI tool with the converted schema
        crew_tool = MCPTool(
            name=tool_name,
            description=tool.description,
            args_schema=args_schema,
        )
        
        crew_tool._client = client
        crew_tool._tool_name = tool_name
        
        crew_tools.append(crew_tool)
    
    return crew_tools

def _convert_json_schema_to_pydantic(schema: Dict[str, Any], model_name: str = "DynamicModel") -> Type[BaseModel]:
    """Convert a JSON schema dictionary into a Pydantic model."""
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    fields = {}
    for field_name, field_schema in properties.items():
        field_type = _get_field_type(field_schema)
        
        # Handle default values correctly
        default = field_schema.get("default", None)
        if field_name in required:
            # Required fields don't get a default
            fields[field_name] = (field_type, ...)
        else:
            # Optional fields with or without default
            fields[field_name] = (Optional[field_type], default)
    
    return create_model(model_name, **fields)

def _get_field_type(field_schema: Dict[str, Any]) -> Type:
    """Convert JSON schema type to Python type."""
    schema_type = field_schema.get("type", "string")
    
    if schema_type == "array":
        items = field_schema.get("items", {})
        item_type = _get_field_type(items)
        return List[item_type]
    
    elif schema_type == "object":
        # Handle nested objects by creating a new model
        return _convert_json_schema_to_pydantic(field_schema, "NestedModel")
    
    # Basic type mapping
    type_mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
    }
    return type_mapping.get(schema_type, str)
