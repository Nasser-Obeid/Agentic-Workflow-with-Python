"""
Code Executor Tool with Output Comparison
Add this to: src/tools/code_executor.py
"""

import sys
from io import StringIO
import signal
import resource
import json
from typing import Dict
from difflib import SequenceMatcher


class SafeCodeExecutor:
    """Safely execute user-provided Python code with output capture and restrictions."""
    
    def __init__(self, timeout=5, memory_limit=50):
        """
        Initialize the executor.
        
        Args:
            timeout: Maximum execution time in seconds (default: 5)
            memory_limit: Maximum memory in MB (default: 50)
        """
        self.timeout = timeout
        self.memory_limit = memory_limit * 1024 * 1024  # Convert to bytes
        self.blocked_modules = {
            'os', 'subprocess', 'sys', 'socket', 'urllib', 'requests',
            'shutil', 'pickle', 'shelve', '__import__', 'eval', 'exec',
            'compile', 'open', 'file', 'input', 'raw_input'
        }
    
    def _timeout_handler(self, signum, frame):
        """Handle timeout signal."""
        raise TimeoutError(f"Code execution exceeded {self.timeout} seconds")
    
    def _set_limits(self):
        """Set resource limits for execution."""
        try:
            # Set memory limit (Unix-like systems only)
            resource.setrlimit(resource.RLIMIT_AS, (self.memory_limit, self.memory_limit))
        except (ValueError, resource.error, AttributeError):
            pass  # Resource limits not supported on this platform
    
    def _create_safe_globals(self):
        """Create a restricted global namespace."""
        safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
            'chr': chr, 'dict': dict, 'enumerate': enumerate, 'filter': filter,
            'float': float, 'format': format, 'hex': hex, 'int': int,
            'isinstance': isinstance, 'len': len, 'list': list, 'map': map,
            'max': max, 'min': min, 'ord': ord, 'pow': pow, 'print': print,
            'range': range, 'reversed': reversed, 'round': round, 'set': set,
            'sorted': sorted, 'str': str, 'sum': sum, 'tuple': tuple,
            'type': type, 'zip': zip
        }
        return {'__builtins__': safe_builtins}
    
    def execute(self, code):
        """
        Execute user code safely and return output, errors, and result.
        
        Args:
            code: String containing Python code to execute
            
        Returns:
            dict: Contains 'output', 'errors', 'success', and 'message' keys
        """
        # Create StringIO objects to capture output
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        # Store original streams
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        result = {
            'output': '',
            'errors': '',
            'success': False,
            'message': ''
        }
        
        try:
            # Basic validation
            if not code or not isinstance(code, str):
                result['message'] = 'Invalid code input'
                return result
            
            # Check for blocked keywords
            code_lower = code.lower()
            for blocked in self.blocked_modules:
                if blocked in code_lower:
                    result['message'] = f'Blocked operation detected: {blocked}'
                    return result
            
            # Set timeout (Unix-like systems only)
            try:
                signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(self.timeout)
            except (AttributeError, ValueError):
                pass  # Signal not supported on this platform
            
            # Set resource limits
            self._set_limits()
            
            # Redirect stdout and stderr
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # Create safe execution environment
            safe_globals = self._create_safe_globals()
            safe_locals = {}
            
            # Execute the code
            exec(code, safe_globals, safe_locals)
            
            result['success'] = True
            result['message'] = 'Code executed successfully'
            
        except TimeoutError as e:
            result['message'] = str(e)
        except MemoryError:
            result['message'] = 'Memory limit exceeded'
        except SyntaxError as e:
            result['message'] = f'Syntax error: {str(e)}'
        except Exception as e:
            result['message'] = f'Execution error: {type(e).__name__}: {str(e)}'
        finally:
            # Cancel alarm
            try:
                signal.alarm(0)
            except (AttributeError, ValueError):
                pass
            
            # Restore stdout and stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            
            # Capture output and errors
            result['output'] = stdout_capture.getvalue()
            result['errors'] = stderr_capture.getvalue()
            
            # Close StringIO objects
            stdout_capture.close()
            stderr_capture.close()
        
        return result


class CodeExecutorTool:
    """
    Tool wrapper for code execution with output comparison
    This integrates with the agent's tool system
    """
    
    def __init__(self, timeout=5, memory_limit=50):
        """
        Initialize the code executor tool
        
        Args:
            timeout: Maximum execution time in seconds
            memory_limit: Maximum memory in MB
        """
        self.executor = SafeCodeExecutor(timeout=timeout, memory_limit=memory_limit)
    
    def execute_and_compare(self, input_data: str) -> Dict:
        """
        Execute code and compare output with expected result
        
        Input format (JSON string):
        {
            "code": "print('Hello')",
            "expected_output": "Hello\n",
            "compare_mode": "exact"  // or "fuzzy", "contains"
        }
        
        Args:
            input_data: JSON string with code and expected output
            
        Returns:
            Dictionary with execution results and comparison
        """
        try:
            # Parse input data
            data = json.loads(input_data)
            code = data.get('code', '')
            expected_output = data.get('expected_output', None)
            compare_mode = data.get('compare_mode', 'exact')
            
            print(f"🔧 Executing code ({len(code)} chars)...")
            
            # Execute the code
            exec_result = self.executor.execute(code)
            
            # Build response
            result = {
                "code": code,
                "execution_success": exec_result['success'],
                "output": exec_result['output'],
                "errors": exec_result['errors'],
                "message": exec_result['message'],
                "expected_output": expected_output,
                "comparison": None
            }
            
            # If expected output is provided, compare
            if expected_output is not None and exec_result['success']:
                comparison = self._compare_outputs(
                    exec_result['output'],
                    expected_output,
                    compare_mode
                )
                result["comparison"] = comparison
            
            return result
            
        except json.JSONDecodeError:
            # If not JSON, treat as simple code execution
            return self.execute_simple(input_data)
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool error: {str(e)}"
            }
    
    def execute_simple(self, code: str) -> Dict:
        """
        Simple code execution without comparison
        
        Args:
            code: Python code to execute
            
        Returns:
            Dictionary with execution results
        """
        print(f"🔧 Executing code (simple mode)...")
        
        exec_result = self.executor.execute(code)
        
        return {
            "code": code,
            "execution_success": exec_result['success'],
            "output": exec_result['output'],
            "errors": exec_result['errors'],
            "message": exec_result['message']
        }
    
    def _compare_outputs(self, actual: str, expected: str, mode: str = 'exact') -> Dict:
        """
        Compare actual output with expected output
        
        Args:
            actual: Actual output from code execution
            expected: Expected output
            mode: Comparison mode ('exact', 'fuzzy', 'contains')
            
        Returns:
            Dictionary with comparison results
        """
        comparison = {
            "mode": mode,
            "match": False,
            "similarity": 0.0,
            "details": ""
        }
        
        # Strip trailing whitespace for comparison
        actual_stripped = actual.strip()
        expected_stripped = expected.strip()
        
        if mode == 'exact':
            # Exact string match
            comparison["match"] = actual_stripped == expected_stripped
            comparison["similarity"] = 1.0 if comparison["match"] else 0.0
            
            if comparison["match"]:
                comparison["details"] = "✅ Output matches exactly!"
            else:
                comparison["details"] = self._create_diff_message(
                    actual_stripped, 
                    expected_stripped
                )
        
        elif mode == 'fuzzy':
            # Fuzzy matching using similarity ratio
            similarity = SequenceMatcher(None, actual_stripped, expected_stripped).ratio()
            comparison["similarity"] = similarity
            comparison["match"] = similarity >= 0.8  # 80% similarity threshold
            
            if comparison["match"]:
                comparison["details"] = f"✅ Output matches with {similarity*100:.1f}% similarity"
            else:
                comparison["details"] = f"❌ Output only {similarity*100:.1f}% similar. Expected at least 80%."
        
        elif mode == 'contains':
            # Check if expected output is contained in actual output
            comparison["match"] = expected_stripped in actual_stripped
            
            if comparison["match"]:
                comparison["details"] = "✅ Output contains expected text!"
            else:
                comparison["details"] = f"❌ Output does not contain expected text: '{expected_stripped}'"
        
        else:
            comparison["details"] = f"Unknown comparison mode: {mode}"
        
        return comparison
    
    def _create_diff_message(self, actual: str, expected: str) -> str:
        """
        Create a detailed difference message
        
        Args:
            actual: Actual output
            expected: Expected output
            
        Returns:
            String describing the differences
        """
        # Show first 200 chars of each
        actual_preview = actual[:200] + "..." if len(actual) > 200 else actual
        expected_preview = expected[:200] + "..." if len(expected) > 200 else expected
        
        message = "❌ Output does not match!\n\n"
        message += f"Expected:\n{expected_preview}\n\n"
        message += f"Got:\n{actual_preview}\n\n"
        
        # Calculate similarity
        similarity = SequenceMatcher(None, actual, expected).ratio()
        message += f"Similarity: {similarity*100:.1f}%"
        
        return message


# Function to register with ToolRegistry
def create_code_executor_tool():
    """
    Factory function to create a code executor tool instance
    This can be called from tool_registry.py
    
    Returns:
        Callable that matches the tool signature
    """
    executor_tool = CodeExecutorTool(timeout=5, memory_limit=50)
    
    def tool_function(input_data: str) -> Dict:
        """
        Tool function for code execution with comparison
        
        Args:
            input_data: Either JSON string or plain code
            
        Returns:
            Execution and comparison results
        """
        return executor_tool.execute_and_compare(input_data)
    
    return tool_function