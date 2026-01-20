# Example MCP Client Configurations

This file shows how to configure various MCP clients to use the SCPI converter server.

## Claude Desktop

**Location:** 
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "scpi-converter": {
      "command": "python3",
      "args": ["-m", "mcp_tools.scpi_converter_server"],
      "cwd": "/home/user/projects/PySCPI",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## Cline (VS Code Extension)

**Location:** VS Code Settings → Extensions → Cline → MCP Servers

**Configuration:**
```json
{
  "mcp.servers": {
    "scpi-converter": {
      "command": "python3",
      "args": ["-m", "mcp_tools.scpi_converter_server"],
      "cwd": "${workspaceFolder}",
      "description": "SCPI C++ to Python converter"
    }
  }
}
```

## Generic MCP Client

For any MCP-compatible client:

```json
{
  "servers": {
    "scpi-converter": {
      "command": "python3",
      "args": ["-m", "mcp_tools.scpi_converter_server"],
      "cwd": "/absolute/path/to/PySCPI",
      "protocol": "stdio",
      "transport": "stdio"
    }
  }
}
```

## Environment Variables

You may need to set these environment variables:

- `PYTHONPATH`: Should include the PySCPI directory
- `PATH`: Should include Python 3.7+

Example with environment:
```json
{
  "mcpServers": {
    "scpi-converter": {
      "command": "python3",
      "args": ["-m", "mcp_tools.scpi_converter_server"],
      "cwd": "/home/user/projects/PySCPI",
      "env": {
        "PYTHONPATH": "/home/user/projects/PySCPI",
        "PATH": "/usr/bin:/usr/local/bin"
      }
    }
  }
}
```

## Testing the Configuration

After adding the configuration:

1. Restart your MCP client
2. Check the logs for any errors
3. Try a simple command: "List available MCP tools"
4. You should see: `convert_file` and `extract_function_info`

## Troubleshooting

### Server doesn't appear
- Check the `cwd` path is absolute and correct
- Verify Python is installed and in PATH
- Check MCP client logs for startup errors

### Permission denied
- Ensure the script has execute permissions
- Try using `python3` instead of `python`
- Check file paths don't contain spaces (or escape them)

### Import errors
- Set `PYTHONPATH` to the PySCPI directory
- Verify all files in `mcp_tools/` are present
- Run `python3 -m mcp_tools.scpi_converter_server` manually to test

## Usage After Setup

Once configured, you can use natural language with your AI assistant:

**Examples:**
- "Convert ScpiMld.cpp to Python stubs"
- "Extract details for the getTxPackets function"
- "Generate stubs for all missing functions in ScpiOtn.py"
- "What C++ implementation details are available for setFramesize?"

The AI will automatically use the appropriate tool based on your request.
