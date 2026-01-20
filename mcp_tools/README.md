# MCP Server for SCPI C++ to Python Conversion

This directory contains an MCP (Model Context Protocol) server that provides tools for converting C++ SCPI implementation files to Python stub implementations.

## Overview

The MCP server provides automated tools to:
- Convert entire C++ SCPI files to Python stub implementations
- Extract implementation details from specific C++ functions
- Generate stubs following the established template patterns

## Setup

### Prerequisites

- Python 3.7+
- MCP-compatible client (like Claude Desktop, Cline, etc.)

### Installation

1. Add the server configuration to your MCP client's config file (typically `~/.config/mcp/config.json` or similar):

```json
{
  "mcpServers": {
    "scpi-converter": {
      "command": "python",
      "args": ["-m", "mcp_tools.scpi_converter_server"],
      "cwd": "/path/to/PySCPI",
      "description": "MCP server for converting C++ SCPI files to Python stub implementations"
    }
  }
}
```

2. Or use the provided configuration file:

```bash
cp mcp-server-config.json ~/.config/mcp/scpi-converter.json
```

## Available Tools

### 1. convert_file

Converts a complete C++ SCPI file to Python stub implementations.

**Parameters:**
- `cpp_file_path` (string, required): Path to the C++ source file
- `py_file_path` (string, required): Path to the Python file with commandTable
- `class_name` (string, optional): Python class name (default: "ScpiPacket")

**Returns:**
```json
{
  "success": true,
  "total_functions": 780,
  "already_defined": 45,
  "missing_functions": 735,
  "stubs_generated": 735,
  "stubs": "... generated stub code ..."
}
```

**Example usage in MCP client:**
```
Use the convert_file tool to convert ScpiMld.cpp to Python stubs for ScpiMld.py
```

### 2. extract_function_info

Extracts implementation details for a specific C++ function.

**Parameters:**
- `cpp_file_path` (string, required): Path to the C++ source file
- `function_name` (string, required): Name of the function to extract

**Returns:**
```json
{
  "success": true,
  "function_info": {
    "comment": "RES:RXBCAST?",
    "has_parameters": false,
    "uses_statistics": true,
    "uses_stream_stats": false,
    "uses_settings": false,
    "is_setter": false,
    "is_getter": true,
    "format_spec": "%I64u"
  }
}
```

**Example usage in MCP client:**
```
Use the extract_function_info tool to get details about the getRxbCast function from ScpiPacket.cpp
```

## Usage Examples

### Converting a new SCPI file

1. Make sure you have both the C++ source file (e.g., `ScpiMld.cpp`) and the Python file with commandTable (e.g., `ScpiMld.py`)

2. Use the MCP client to call the convert_file tool:
   ```
   Convert ScpiMld.cpp to Python stubs for ScpiMld.py using the ScpiMld class
   ```

3. The tool will:
   - Analyze the commandTable in the Python file
   - Find all missing function implementations
   - Extract C++ implementation details for each function
   - Generate stub functions following the template pattern
   - Return the generated stubs

4. Insert the generated stubs into your Python file before the commandTable

### Getting information about a specific function

If you want to understand a specific C++ function before implementing it:

```
Extract implementation details for the getTxPackets function from ScpiPacket.cpp
```

This will return all the relevant C++ implementation details that can guide the Python implementation.

## File Structure

```
mcp_tools/
├── __init__.py                  # Package initialization
├── scpi_converter_server.py     # Main MCP server implementation
└── README.md                     # This file
```

## Stub Template Pattern

All generated stubs follow this pattern (based on getRxbCast):

```python
def functionName(self, parameters):
    """**SCPI:COMMAND** - functionName command.
    
    C++ Implementation Details:
    - Uses callGetPacketStatistics() to get IdlPacket2Stats structure
    - Returns idlStatPacket.fieldName field
    - Format: unsigned 64-bit integer ("%I64u")
    - No parameters required
    
    Python TODO:
    - Call veexlib packet statistics method
    - Return fieldName count as bytes
    """
    response = None
    # TODO: Implement functionName
    return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
```

## Troubleshooting

### Server not appearing in MCP client

1. Check that the `cwd` path in the configuration is correct
2. Ensure Python is in your PATH
3. Verify the server script is executable: `python -m mcp_tools.scpi_converter_server`

### Conversion errors

If you get conversion errors:
1. Verify the C++ file path is correct
2. Ensure the Python file has a `commandTable = [...]` section
3. Check that the class name matches the actual class in the Python file

### Function not found in C++

Some functions may not be in the C++ file:
- They might be defined in a different C++ file
- They might be template-generated functions
- They might use different naming conventions

The tool will still generate a basic stub with a note that the C++ implementation wasn't found.

## Future Enhancements

Potential improvements:
- Support for multiple C++ files
- Better handling of template functions
- Integration with git to directly commit stubs
- Support for partial implementations (not just stubs)
- Validation of generated stubs

## Contributing

When adding new features to the MCP server:
1. Update the capabilities in `run_server()`
2. Add new tool handlers
3. Update this README with usage examples
4. Test with actual SCPI files

## License

Same as the PySCPI project.
