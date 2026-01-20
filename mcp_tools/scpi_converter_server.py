"""
MCP Server for SCPI C++ to Python Converter

This MCP server provides tools for converting C++ SCPI implementation files
to Python stub implementations, following the established template patterns.
"""

import json
import sys
import re
from typing import Any, Dict, List, Optional
from pathlib import Path

# MCP Protocol utilities
def send_response(response: Dict[str, Any]) -> None:
    """Send a JSON-RPC response to stdout."""
    print(json.dumps(response), flush=True)

def read_request() -> Dict[str, Any]:
    """Read a JSON-RPC request from stdin."""
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)

# Core conversion functions
def extract_cpp_function_info(cpp_content: str, func_name: str) -> Optional[Dict[str, Any]]:
    """Extract information about a function from C++ code."""
    cpp_pattern = rf'void ScpiPacket::{func_name}\s*\([^)]*\)'
    match = re.search(cpp_pattern, cpp_content)
    
    if not match:
        return None
    
    start_pos = match.start()
    end_pos = match.end()
    
    # Look for comment before function
    comment_start = cpp_content.rfind('//', max(0, start_pos - 200), start_pos)
    comment = ""
    if comment_start != -1:
        comment_end = cpp_content.find('\n', comment_start)
        comment = cpp_content[comment_start:comment_end].strip()
        comment = comment.replace('//', '').replace('*', '').strip()
    
    # Get function body
    body_end = min(end_pos + 1000, len(cpp_content))
    body = cpp_content[end_pos:body_end]
    
    # Check for common patterns
    info = {
        'comment': comment,
        'has_parameters': 'CString&' in cpp_content[start_pos:end_pos],
        'uses_statistics': 'callGetPacketStatistics' in body or 'IdlPacket2Stats' in body,
        'uses_stream_stats': 'callGetPacketStreamStatistics' in body,
        'uses_settings': 'callGetAllSettings' in body or 'callGetAllowedSettings' in body,
        'is_setter': func_name.startswith('set') or func_name.startswith('tx') and 'Set' in func_name,
        'is_getter': func_name.startswith('get') or '?' in comment,
        'format_spec': None
    }
    
    # Try to find format specifier
    format_match = re.search(r'Format\("([^"]+)"', body)
    if format_match:
        info['format_spec'] = format_match.group(1)
    
    return info

def generate_stub_function(func_name: str, commands: List[str], cpp_info: Optional[Dict[str, Any]]) -> str:
    """Generate a stub function following the getRxbCast template."""
    
    command_str = commands[0] if commands else func_name
    if len(commands) > 1:
        command_list = "\n        Also used for:\n" + "\n".join(f"        - {cmd}" for cmd in commands[1:])
    else:
        command_list = ""
    
    # Build C++ implementation details
    cpp_details = []
    if cpp_info:
        if cpp_info.get('uses_statistics'):
            cpp_details.append("- Uses callGetPacketStatistics() to get IdlPacket2Stats structure")
        if cpp_info.get('uses_stream_stats'):
            cpp_details.append("- Uses callGetPacketStreamStatistics() to get stream statistics")
        if cpp_info.get('uses_settings'):
            cpp_details.append("- Uses callGetAllSettings() and/or callGetAllowedSettings()")
        if cpp_info.get('format_spec'):
            cpp_details.append(f"- Format: {cpp_info['format_spec']}")
        if cpp_info.get('has_parameters'):
            cpp_details.append("- Takes parameters from command string")
        else:
            cpp_details.append("- No parameters required")
    else:
        cpp_details.append("- C++ implementation not found")
        cpp_details.append("- Check C++ source for implementation details")
    
    cpp_details_str = "\n        ".join(cpp_details)
    
    # Build Python TODO section
    if cpp_info and cpp_info.get('is_getter'):
        todo = ["- Implement query logic",
                "- Call appropriate veexlib method",
                "- Return result as bytes"]
    elif cpp_info and cpp_info.get('is_setter'):
        todo = ["- Parse parameters using ParseUtils.preParseParameters()",
                "- Validate parameter values",
                "- Call appropriate veexlib method to set value",
                "- Return None on success or error response"]
    else:
        todo = ["- Implement command logic",
                "- Follow C++ implementation pattern"]
    
    todo_str = "\n        ".join(todo)
    
    stub = f'''    def {func_name}(self, parameters):
        """**{command_str}** - {func_name} command.{command_list}
        
        C++ Implementation Details:
        {cpp_details_str}
        
        Python TODO:
        {todo_str}
        """
        response = None
        # TODO: Implement {func_name}
        return self._errorResponse(ScpiErrorCode.INVALID_RESULTS)
'''
    
    return stub

def convert_file_to_stubs(cpp_file_path: str, py_file_path: str, class_name: str) -> Dict[str, Any]:
    """
    Convert a C++ SCPI file to Python stubs.
    
    Args:
        cpp_file_path: Path to the C++ source file
        py_file_path: Path to the Python file with commandTable
        class_name: Name of the Python class (e.g., 'ScpiPacket')
    
    Returns:
        Dictionary with conversion results
    """
    try:
        # Read files
        with open(cpp_file_path, 'r') as f:
            cpp_content = f.read()
        
        with open(py_file_path, 'r') as f:
            py_content = f.read()
        
        # Extract commandTable
        start = py_content.find('commandTable = [')
        if start == -1:
            return {'error': 'commandTable not found in Python file'}
        
        end = py_content.find(']', start) + 1
        commandTable_section = py_content[start:end]
        
        # Get all commands and functions
        pattern = rf'Cmnd\(b"([^"]+)",\s*{class_name}\.(\w+)\)'
        commands_and_functions = re.findall(pattern, commandTable_section)
        
        # Group by function
        function_commands = {}
        for command, func in commands_and_functions:
            if func not in function_commands:
                function_commands[func] = []
            function_commands[func].append(command)
        
        # Get already defined functions
        class_section = py_content[:start]
        defined_pattern = r'def (\w+)\(self'
        defined_functions = set(re.findall(defined_pattern, class_section))
        
        # Get missing functions
        missing_functions = sorted([f for f in function_commands.keys() if f not in defined_functions])
        
        # Generate stubs
        stubs = []
        for func in missing_functions:
            commands = function_commands[func]
            cpp_info = extract_cpp_function_info(cpp_content, func)
            stub = generate_stub_function(func, commands, cpp_info)
            stubs.append(stub)
        
        return {
            'success': True,
            'total_functions': len(function_commands),
            'already_defined': len([f for f in function_commands.keys() if f in defined_functions]),
            'missing_functions': len(missing_functions),
            'stubs_generated': len(stubs),
            'stubs': '\n'.join(stubs)
        }
    
    except Exception as e:
        return {'error': str(e)}

# MCP Tool handlers
def handle_convert_file(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the convert_file tool call."""
    cpp_file = params.get('cpp_file_path')
    py_file = params.get('py_file_path')
    class_name = params.get('class_name', 'ScpiPacket')
    
    if not cpp_file or not py_file:
        return {'error': 'cpp_file_path and py_file_path are required'}
    
    result = convert_file_to_stubs(cpp_file, py_file, class_name)
    return result

def handle_extract_function_info(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the extract_function_info tool call."""
    cpp_file = params.get('cpp_file_path')
    func_name = params.get('function_name')
    
    if not cpp_file or not func_name:
        return {'error': 'cpp_file_path and function_name are required'}
    
    try:
        with open(cpp_file, 'r') as f:
            cpp_content = f.read()
        
        info = extract_cpp_function_info(cpp_content, func_name)
        if info:
            return {'success': True, 'function_info': info}
        else:
            return {'error': f'Function {func_name} not found in C++ file'}
    
    except Exception as e:
        return {'error': str(e)}

# MCP Server main loop
def run_server():
    """Main MCP server loop."""
    # Send server capabilities
    capabilities = {
        'jsonrpc': '2.0',
        'id': 0,
        'result': {
            'capabilities': {
                'tools': {
                    'convert_file': {
                        'description': 'Convert a C++ SCPI file to Python stub implementations',
                        'parameters': {
                            'cpp_file_path': {'type': 'string', 'description': 'Path to C++ source file'},
                            'py_file_path': {'type': 'string', 'description': 'Path to Python file with commandTable'},
                            'class_name': {'type': 'string', 'description': 'Python class name (default: ScpiPacket)'}
                        }
                    },
                    'extract_function_info': {
                        'description': 'Extract implementation details for a specific C++ function',
                        'parameters': {
                            'cpp_file_path': {'type': 'string', 'description': 'Path to C++ source file'},
                            'function_name': {'type': 'string', 'description': 'Name of the function to extract'}
                        }
                    }
                }
            }
        }
    }
    
    while True:
        request = read_request()
        if request is None:
            break
        
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')
        
        if method == 'tools/call':
            tool_name = params.get('name')
            tool_params = params.get('arguments', {})
            
            if tool_name == 'convert_file':
                result = handle_convert_file(tool_params)
            elif tool_name == 'extract_function_info':
                result = handle_extract_function_info(tool_params)
            else:
                result = {'error': f'Unknown tool: {tool_name}'}
            
            response = {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': result
            }
            send_response(response)

if __name__ == '__main__':
    run_server()
