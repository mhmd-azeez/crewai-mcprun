from typing import Type, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from crewai.tools import BaseTool
import extism
import json

class CryptoHashInput(BaseModel):
    """Input schema for CryptoHashTool."""
    hash_type: str = Field(..., description="Type of hash to generate (md5, sha1, sha256, bcrypt)")
    text: str = Field(..., description="Text to hash")
    cost: Optional[int] = Field(None, description="Cost factor for bcrypt (4-31, default: 10)")

class CryptoHashTool(BaseTool):
    """Tool for generating cryptographic hashes using the Crypto hash servlet."""
    name: str = "crypto_hash"
    description: str = "Generate cryptographic hashes using various algorithms (MD5, SHA-1, SHA-256, bcrypt)"
    args_schema: Type[BaseModel] = CryptoHashInput
    wasm_path: str = Field(..., description="Path to the WASM file")
    plugin: Optional[extism.Plugin] = Field(None, description="Extism plugin instance")
    tool_schemas: Dict[str, Any] = Field(default_factory=dict, description="Tool schemas from WASM module")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, wasm_path: str, **data):
        """Initialize the tool with path to the WASM file."""
        super().__init__(wasm_path=wasm_path, **data)
        # Load the plugin once during initialization
        self.plugin = extism.Plugin({"wasm": [{"path": self.wasm_path}]}, wasi=True)
        # Get tool descriptions for validation
        self._load_tool_descriptions()

    def _load_tool_descriptions(self):
        """Load and parse tool descriptions from the WASM module."""
        try:
            # Call describe() function and parse response
            result = self.plugin.call("describe", "")
            tools_result = json.loads(result)
            
            # Create lookup of valid tools and their schemas
            self.tool_schemas = {
                tool["name"]: tool["inputSchema"]
                for tool in tools_result.get("tools", [])
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to load tool descriptions: {str(e)}")

    def _validate_hash_type(self, hash_type: str):
        """Validate that the requested hash type is supported."""
        if hash_type not in self.tool_schemas:
            valid_types = list(self.tool_schemas.keys())
            raise ValueError(f"Invalid hash type '{hash_type}'. Must be one of: {valid_types}")

    def _prepare_arguments(self, hash_type: str, text: str, cost: Optional[int] = None) -> Dict[str, Any]:
        """Prepare arguments based on hash type."""
        if hash_type == "bcrypt":
            args = {"password": text}
            if cost is not None:
                args["cost"] = cost
            return args
        return {"text": text}

    def _run(self, hash_type: str, text: str, cost: Optional[int] = None) -> str:
        """
        Execute the hash generation using the WASM module.
        
        Args:
            hash_type: Type of hash to generate (md5, sha1, sha256, bcrypt)
            text: Text to hash
            cost: Optional cost factor for bcrypt

        Returns:
            str: The generated hash
        
        Raises:
            ValueError: If the hash type is invalid
            RuntimeError: If the hash generation fails
        """
        try:
            # Validate hash type
            self._validate_hash_type(hash_type)
            
            # Prepare request arguments
            args = self._prepare_arguments(hash_type, text, cost)
            
            # Prepare the full request
            request = {
                "params": {
                    "name": hash_type,
                    "arguments": args
                }
            }
            
            # Call the WASM function
            result = self.plugin.call("call", json.dumps(request))
            response = json.loads(result)
            
            # Extract hash from response
            if not response.get("content"):
                raise RuntimeError("No content in response")
            
            content = response["content"][0]
            if content.get("type") != "text" or not content.get("text"):
                raise RuntimeError("Invalid response format")
            
            return content["text"]
            
        except Exception as e:
            raise RuntimeError(f"Hash generation failed: {str(e)}")

    def __del__(self):
        """Cleanup when the tool is destroyed."""
        if hasattr(self, 'plugin'):
            del self.plugin