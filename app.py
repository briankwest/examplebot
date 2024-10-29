from flask import Flask, request, jsonify, send_file
import os
from dotenv import load_dotenv
from flask_httpauth import HTTPBasicAuth

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Example environment variable
EXAMPLE_VAR = os.getenv('EXAMPLE_VAR')
HTTP_USERNAME = os.getenv('HTTP_USERNAME')
HTTP_PASSWORD = os.getenv('HTTP_PASSWORD')

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == HTTP_USERNAME and password == HTTP_PASSWORD:
        return True
    return False

# Define a function that uses various argument types
def comprehensive_function(string_arg, integer_arg, boolean_arg, array_arg, object_arg):
    # Process string argument
    print(f"String Argument: {string_arg}")

    # Process integer argument
    print(f"Integer Argument: {integer_arg}")

    # Process boolean argument
    print(f"Boolean Argument: {boolean_arg}")

    # Process array argument
    print("Array Argument:")
    for item in array_arg:
        print(f" - {item}")

    # Process object argument
    print("Object Argument:")
    print(f"Nested String: {object_arg['nested_string']}")
    print(f"Nested Integer: {object_arg['nested_integer']}")

    # Return a summary
    return {
        "response": "Function executed successfully with all argument types."
    }

# Define function signatures
FUNCTION_SIGNATURES = {
    "comprehensive_function": {
        "purpose": "Demonstrate handling of various argument types",
        "function": "comprehensive_function",
        "argument": {
            "type": "object",
            "properties": {
                "string_arg": {"type": "string", "description": "A simple string argument."},
                "integer_arg": {"type": "integer", "description": "An integer argument."},
                "boolean_arg": {"type": "boolean", "description": "A boolean argument."},
                "array_arg": {"type": "array", "items": {"type": "string"}, "description": "An array of strings."},
                "object_arg": {
                    "type": "object",
                    "properties": {
                        "nested_string": {"type": "string", "description": "A nested string within an object."},
                        "nested_integer": {"type": "integer", "description": "A nested integer within an object."}
                    },
                    "required": ["nested_string", "nested_integer"],
                    "description": "An object containing nested properties."
                }
            },
            "required": ["string_arg", "integer_arg", "boolean_arg", "array_arg", "object_arg"]
        }
    }
}

@app.route('/swaig', methods=['POST'])
@auth.verify_password
def swaig_handler():
    data = request.json
    action = data.get('action')
    print(f"Received action: {action}")

    if action == "get_signature":
        requested_functions = data.get("functions", list(FUNCTION_SIGNATURES.keys()))
        response = [
            FUNCTION_SIGNATURES[func] 
            for func in requested_functions 
            if func in FUNCTION_SIGNATURES
        ]

        missing_functions = [
            func for func in requested_functions 
            if func not in FUNCTION_SIGNATURES
        ]

        print(f"missing_functions: {missing_functions}")

        return jsonify(response)

    else:
        function_name = data.get('function')
        print(f"Function name: {function_name}")
        argument = data.get('argument', {})
        params = argument.get('parsed', [{}])[0]
        print(f"Function name: {function_name}, Params: {params}")

        function_map = {
            func_name: globals()[func_name] 
            for func_name in FUNCTION_SIGNATURES.keys() 
            if func_name in globals()
        }
        print(f"Available functions: {list(function_map.keys())}")

        if function_name in function_map:
            try:
                response = function_map[function_name](**params)
                return jsonify({"response": response})
            except TypeError as e:
                return jsonify({"error": f"Invalid parameters for function '{function_name}'"}), 400
            except Exception as e:
                return jsonify({"error": "An unexpected error occurred"}), 500
        else:
            return jsonify({"error": "Function not found"}), 404

@app.route('/', methods=['GET'])
@app.route('/swaig', methods=['GET'])
def serve_example_html():
    try:
        return send_file('example.html')
    except Exception as e:
        return jsonify({"error": "Failed to serve example.html"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
