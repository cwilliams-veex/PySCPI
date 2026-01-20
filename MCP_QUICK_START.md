# SCPI C++ to Python Converter - Quick Start Guide

This MCP server automates the conversion of C++ SCPI files to Python stub implementations.

## What is MCP?

Model Context Protocol (MCP) is a standard for connecting AI assistants to external tools and data sources. This server provides tools specifically for SCPI file conversion.

## Quick Setup (3 steps)

### 1. Configure your MCP client

Add this to your MCP client configuration (e.g., Claude Desktop config):

```json
{
  "mcpServers": {
    "scpi-converter": {
      "command": "python",
      "args": ["-m", "mcp_tools.scpi_converter_server"],
      "cwd": "/absolute/path/to/PySCPI",
      "description": "SCPI C++ to Python converter"
    }
  }
}
```

**Important:** Replace `/absolute/path/to/PySCPI` with the actual path to this repository.

### 2. Restart your MCP client

After adding the configuration, restart your MCP-compatible client (Claude Desktop, Cline, etc.)

### 3. Use the tools

Simply ask your AI assistant:

```
"Use the convert_file tool to convert ScpiMld.cpp to Python stubs for ScpiMld.py using the ScpiMld class"
```

or

```
"Extract implementation details for the setFramesize function from ScpiPacket.cpp"
```

## Example Workflows

### Convert an entire file

**Scenario:** You have `ScpiOtn.cpp` and `ScpiOtn.py`, and you want to generate all missing stubs.

**Command to AI:**
```
Convert ScpiOtn.cpp to Python stubs for ScpiOtn.py using the ScpiOtn class. 
Show me the statistics first, then provide the stubs.
```

**What happens:**
1. Tool analyzes ScpiOtn.py's commandTable
2. Identifies missing functions
3. Extracts C++ implementation details
4. Generates stub functions
5. Returns results with statistics

### Get info about one function

**Scenario:** You want to implement `getTxBytes` but need to understand the C++ version first.

**Command to AI:**
```
Extract implementation details for getTxBytes from ScpiPacket.cpp
```

**What happens:**
1. Tool finds the function in C++
2. Extracts: parameters, data structures used, format specifiers, etc.
3. Returns structured information

## Files in Other Directories

### ScpiMld.py and ScpiMld.cpp
These files likely need the same stub generation treatment. Use:
```
Convert ScpiMld.cpp to Python stubs using ScpiMld class
```

### ScpiOtn.py and ScpiOtn.cpp
Another candidate for conversion:
```
Convert ScpiOtn.cpp to Python stubs using ScpiOtn class
```

### ScpiSonetSdh.py
Check if there's a corresponding C++ file and convert as needed.

### ScpiSystem.py
Same - if there's a C++ counterpart, it can be converted.

## Verifying the Installation

Test that the server is working:

```bash
cd /path/to/PySCPI
python -m mcp_tools.scpi_converter_server --test
```

(Note: The server uses stdin/stdout for MCP protocol, so direct testing requires sending JSON-RPC messages)

## Common MCP Clients

- **Claude Desktop**: Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
- **Cline (VS Code)**: Configure in VS Code settings under MCP servers
- **Custom**: Any tool that implements the MCP client protocol

## What Gets Generated

Each stub includes:
- ✅ Function signature with parameters
- ✅ Comprehensive docstring with SCPI command name
- ✅ C++ implementation details (data structures, methods, formats)
- ✅ Python TODO section with implementation guidance
- ✅ Proper error handling

## Need Help?

1. **Server not working?** Check the MCP client logs
2. **Path issues?** Ensure `cwd` is set to the absolute path to PySCPI
3. **Conversion errors?** Verify the C++ and Python files exist and are readable

## Next Steps After Conversion

After generating stubs:
1. Review the generated stubs
2. Insert them into the Python file (before commandTable)
3. Verify Python syntax: `python -m py_compile YourFile.py`
4. Implement actual functionality gradually, using the C++ details as a guide
5. Test each implementation

---

**Pro tip:** Use the MCP server for all SCPI files in this repo that need conversion. It saves hours of manual work!
