import json
import math
from datetime import datetime
import pandas as pd

# Tools
def calculator(expression: str):
    # Restricted namespace
    allowed_names = {"sqrt": math.sqrt, "pow": math.pow, "pi": math.pi}
    # For safety, compile and check names
    code = compile(expression, "<string>", "eval")
    for name in code.co_names:
        if name not in allowed_names:
            raise NameError(f"Use of '{name}' is not allowed in this restricted calculator.")
    return eval(code, {"__builtins__": {}}, allowed_names)

def days_between(d1: str, d2: str):
    date_format = "%Y-%m-%d"
    a = datetime.strptime(d1, date_format)
    b = datetime.strptime(d2, date_format)
    return abs((b - a).days)

def unit_convert(value: float, frm: str, to: str):
    conversions = {
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x / 0.621371,
        ("kg", "lb"): lambda x: x * 2.20462,
        ("lb", "kg"): lambda x: x / 2.20462,
        ("C", "F"): lambda x: (x * 9/5) + 32,
        ("F", "C"): lambda x: (x - 32) * 5/9,
    }
    key = (frm, to)
    if key in conversions:
        return conversions[key](value)
    raise ValueError(f"Unsupported conversion from {frm} to {to}")

def csv_mean(filename: str, column_name: str):
    df = pd.read_csv(filename)
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in {filename}")
    return df[column_name].mean()

# Tool registry
tool_registry = {
    "calculator": calculator,
    "days_between": days_between,
    "unit_convert": unit_convert,
    "csv_mean": csv_mean
}

# Schemas
schemas = [
    {
        "name": "calculator",
        "description": "Evaluates an arithmetic expression in a restricted namespace (sqrt, pow, pi).",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "The arithmetic expression to evaluate."}
            },
            "required": ["expression"]
        }
    },
    {
        "name": "days_between",
        "description": "Calculates the whole number of days between two dates.",
        "parameters": {
            "type": "object",
            "properties": {
                "d1": {"type": "string", "description": "First date (ISO YYYY-MM-DD)"},
                "d2": {"type": "string", "description": "Second date (ISO YYYY-MM-DD)"}
            },
            "required": ["d1", "d2"]
        }
    },
    {
        "name": "unit_convert",
        "description": "Converts a value between km/miles, kg/lb, or C/F.",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": "number", "description": "The value to convert"},
                "frm": {"type": "string", "description": "Source unit (km, miles, kg, lb, C, F)"},
                "to": {"type": "string", "description": "Target unit (km, miles, kg, lb, C, F)"}
            },
            "required": ["value", "frm", "to"]
        }
    },
    {
        "name": "csv_mean",
        "description": "Reads a CSV file and returns the mean of a named column.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Path to the CSV file"},
                "column_name": {"type": "string", "description": "Name of the column"}
            },
            "required": ["filename", "column_name"]
        }
    }
]

# Dispatch function
def dispatch(tool_call_json: str):
    try:
        # Parse JSON
        call = json.loads(tool_call_json)
        
        # Check tool name
        name = call.get("name")
        if not name:
            return {"error": "Missing 'name' in tool call"}
        
        if name not in tool_registry:
            return {"error": f"Unknown tool: {name}"}
            
        args = call.get("arguments", {})
        
        # Invoke function
        func = tool_registry[name]
        try:
            result = func(**args)
            return {"observation": result}
        except TypeError as e:
             return {"error": f"Wrong argument name/type for {name}: {str(e)}"}
        except Exception as e:
            return {"error": f"Exception inside tool {name}: {str(e)}"}
            
    except json.JSONDecodeError as e:
        return {"error": f"Malformed JSON: {str(e)}"}

if __name__ == "__main__":
    with open('output_log.txt', 'w') as f:
        def log_and_print(text):
            print(text)
            f.write(text + '\n')

        log_and_print("=== TOOL SCHEMAS ===")
        log_and_print(json.dumps(schemas, indent=2))
        log_and_print("\n=== RUNNING NORMAL TOOL CALLS ===")
        
        normal_calls = [
            '{"name": "calculator", "arguments": {"expression": "pow(2, 3)"}}',
            '{"name": "days_between", "arguments": {"d1": "2023-01-01", "d2": "2023-01-31"}}',
            '{"name": "unit_convert", "arguments": {"value": 100, "frm": "km", "to": "miles"}}'
        ]
        
        for call in normal_calls:
            log_and_print(f"Tool Call: {call}")
            log_and_print(f"Observation: {json.dumps(dispatch(call))}\n")
            
        log_and_print("=== RUNNING EXERCISE 1 (Error Handling) ===")
        
        error_calls = [
            ('Malformed JSON', '{"name": "calculator", "arguments": {"expression": "pow(2, 3)"}'),
            ('Unknown Tool', '{"name": "unknown_tool", "arguments": {}}'),
            ('Wrong Argument Name', '{"name": "calculator", "arguments": {"expr": "pow(2, 3)"}}'),
            ('Exception inside tool', '{"name": "calculator", "arguments": {"expression": "1 / 0"}}')
        ]
        
        for desc, call in error_calls:
            log_and_print(f"{desc}:")
            log_and_print(f"Tool Call: {call}")
            log_and_print(f"Observation: {json.dumps(dispatch(call))}\n")
            
        log_and_print("=== RUNNING EXERCISE 2 (CSV Mean Tool) ===")
        
        # Create sample CSV
        df = pd.DataFrame({'A': [10, 20, 30], 'B': [1, 2, 3]})
        df.to_csv('data.csv', index=False)
        
        csv_call = '{"name": "csv_mean", "arguments": {"filename": "data.csv", "column_name": "A"}}'
        log_and_print(f"Tool Call: {csv_call}")
        log_and_print(f"Observation: {json.dumps(dispatch(csv_call))}\n")
