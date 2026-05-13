import json
from typing import Dict, Any
from backend.services.db import db


GET_EMPLOYEE_COUNT_DEFINITION = {
    "name": "get_employee_count",
    "description": "Get the total count of employees, optionally filtered by location.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "Filter by location (e.g. 'Gurugram', 'Bangalore'). If not provided, returns total count."
            }
        },
        "required": []
    }
}

FIND_EMPLOYEE_DEFINITION = {
    "name": "find_employee",
    "description": "Find an employee by name and return their details (name, email, location, role). Supports partial name matching.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Employee name or partial name to search for"
            }
        },
        "required": ["name"]
    }
}

LIST_EMPLOYEES_BY_LOCATION_DEFINITION = {
    "name": "list_employees_by_location",
    "description": "List all employees at a given location.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "Location name (e.g. 'Gurugram', 'Bangalore', 'Nagpur')"
            }
        },
        "required": ["location"]
    }
}

TOOLS = [GET_EMPLOYEE_COUNT_DEFINITION, FIND_EMPLOYEE_DEFINITION, LIST_EMPLOYEES_BY_LOCATION_DEFINITION]


def execute_tool(name: str, inputs: Dict[str, Any]) -> str:
    """Execute a tool and return the result as a JSON string."""
    if name == "get_employee_count":
        location = inputs.get("location")
        count = db.count_employees(location)
        if location:
            return f"Total employees in {location}: {count}"
        else:
            return f"Total employees in Habuild: {count}"
    
    elif name == "find_employee":
        employee_name = inputs.get("name")
        if not employee_name:
            return json.dumps({"error": "Name is required"})
        employees = db.find_employee_by_name(employee_name)
        if not employees:
            return json.dumps({"message": f"No employees found with name matching '{employee_name}'"})
        return json.dumps(employees)
    
    elif name == "list_employees_by_location":
        location = inputs.get("location")
        if not location:
            return json.dumps({"error": "Location is required"})
        employees = db.list_employees_by_location(location)
        if not employees:
            return json.dumps({"message": f"No employees found in {location}"})
        return json.dumps(employees)
    
    else:
        return json.dumps({"error": f"Unknown tool: {name}"})
