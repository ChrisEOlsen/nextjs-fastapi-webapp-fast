import os
import docker
from mcp.server.fastmcp import FastMCP
from jinja2 import Environment, FileSystemLoader
from typing import List, Literal
from pydantic import BaseModel

# Initialize FastMCP
mcp = FastMCP("My Custom MCP Server")

# --- Configuration ---
templates_env = Environment(loader=FileSystemLoader("/mcp/templates"))
WORKSPACE_DIR = "/workspace"

# --- Helper Functions ---
def to_pascal_case(snake_case: str) -> str:
    return "".join(word.capitalize() for word in snake_case.split('_'))

def to_plural(snake_case: str) -> str:
    if snake_case.endswith('s'):
        return snake_case + 'es'
    return snake_case + 's'

def type_to_sqlalchemy(field_type: str) -> str:
    mapping = {
        "string": "String", "text": "Text", "integer": "Integer",
        "float": "Float", "boolean": "Boolean", "date": "Date",
        "datetime": "DateTime", "uuid": "Uuid"
    }
    return mapping.get(field_type, "String")

def type_to_pydantic(field_type: str) -> str:
    mapping = {
        "string": "str", "text": "str", "integer": "int",
        "float": "float", "boolean": "bool", "date": "date",
        "datetime": "datetime", "uuid": "UUID"
    }
    return mapping.get(field_type, "str")

def append_to_file(file_path: str, content: str):
    full_path = os.path.join(WORKSPACE_DIR, file_path)
    if os.path.exists(full_path):
        with open(full_path, "a") as f:
            f.write(content)

# --- Define Tools ---

class FieldDefinition(BaseModel):
    name: str
    type: Literal["string", "text", "integer", "float", "boolean", "date", "datetime", "uuid"]
    required: bool = True

@mcp.tool()
def create_resource(resource_name: str, fields: List[FieldDefinition]):
    """
    Scaffolds a new resource (backend models, schemas, crud, endpoints, and frontend pages).
    Args:
        resource_name: The singular snake_case name (e.g., 'product_item').
        fields: A list of field definitions for the resource.
    """
    ctx = {
        "resource_name_snake": resource_name,
        "resource_name_pascal": to_pascal_case(resource_name),
        "resource_name_plural_snake": to_plural(resource_name),
        "resource_name_plural_pascal": to_pascal_case(to_plural(resource_name)),
        "fields": fields
    }

    base_paths = {
        "backend": os.path.join(WORKSPACE_DIR, "backend/app"),
        "frontend": os.path.join(WORKSPACE_DIR, "frontend/src")
    }

    files_to_generate = {
        "backend/model.py.j2": os.path.join(base_paths["backend"], f"models/{ctx['resource_name_snake']}.py"),
        "backend/schema.py.j2": os.path.join(base_paths["backend"], f"db/schemas/{ctx['resource_name_snake']}.py"),
        "backend/crud.py.j2": os.path.join(base_paths["backend"], f"crud/crud_{ctx['resource_name_snake']}.py"),
        "backend/endpoint.py.j2": os.path.join(base_paths["backend"], f"api/v1/endpoints/{ctx['resource_name_plural_snake']}.py"),
        "frontend/api_service.js.j2": os.path.join(base_paths["frontend"], f"services/api/{ctx['resource_name_plural_snake']}.js"),
        "frontend/page.js.j2": os.path.join(base_paths["frontend"], f"app/{ctx['resource_name_plural_snake']}/page.js"),
    }

    generated_list = []
    for template_name, output_path in files_to_generate.items():
        template = templates_env.get_template(template_name)
        
        rendered_content = ""
        # Handle indentations for model and schema
        if "model.py.j2" in template_name:
            # FIX 1: Indentation
            field_lines = [f"{f.name} = Column({type_to_sqlalchemy(f.type)}, nullable={not f.required})" for f in fields]
            replacement = ("\n    ").join(field_lines)
            rendered_content = template.render(ctx).replace("# --- The MCP will add fields here ---", replacement)
            
            # FIX 2: Ensure all SQLAlchemy types are imported so backend doesn't crash
            # We replace the basic import line with one that includes everything
            rendered_content = rendered_content.replace(
                "from sqlalchemy import Column, String, Integer, Text",
                "from sqlalchemy import Column, String, Integer, Text, Boolean, Float, Date, DateTime, Uuid"
            )

        elif "schema.py.j2" in template_name:
            field_lines = [f"{f.name}: {type_to_pydantic(f.type)}{' | None' if not f.required else ''}" for f in fields]
            replacement = ("\n    ").join(field_lines)
            rendered_content = template.render(ctx).replace("# --- The MCP will add fields here ---", replacement)
        else:
            rendered_content = template.render(ctx)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(rendered_content)
        
        # FIX 3: Fix permissions so you can edit/delete files on host
        try:
            os.chmod(output_path, 0o666)
        except Exception:
            pass # Ignore if fails
            
        generated_list.append(output_path)

    # Modify existing files
    append_to_file("backend/app/models/__init__.py", f"\nfrom .{ctx['resource_name_snake']} import {ctx['resource_name_pascal']}")
    append_to_file("backend/app/api/v1/routers.py", f"\napi_router.include_router({ctx['resource_name_plural_snake']}.router, prefix='/{ctx['resource_name_plural_snake']}', tags=['{ctx['resource_name_pascal']}'])")

    return f"Created resource {resource_name}. Generated files: {generated_list}"

@mcp.tool()
def create_frontend_component(component_name: str, path: str, prompt: str):
    """
    Creates a new React frontend component based on a prompt.
    Args:
        component_name: PascalCase name (e.g. 'UserProfile').
        path: Relative path from frontend/src/components.
        prompt: Description of what the component should do.
    """
    ctx = {"resource_name_pascal": component_name, "prompt": prompt}
    template = templates_env.get_template("frontend/component.js.j2")
    rendered_content = template.render(ctx)

    output_path = os.path.join(WORKSPACE_DIR, "frontend/src/components", path, f"{component_name}.js")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(rendered_content)
    
    # Fix permissions
    try:
        os.chmod(output_path, 0o666)
    except Exception:
        pass

    return f"Component {component_name} created at {output_path}"

@mcp.tool()
def apply_migrations(message: str = "Applied migrations via MCP"):
    """
    Runs database migrations (Alembic) inside the backend container.
    """
    client = docker.from_env()
    try:
        backend = client.containers.get("backend")
        
        exit_code, output = backend.exec_run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            workdir="/code"
        )
        if exit_code != 0:
            return f"Error creating revision: {output.decode()}"

        exit_code, output = backend.exec_run(
            ["alembic", "upgrade", "head"],
            workdir="/code"
        )
        if exit_code != 0:
            return f"Error applying migration: {output.decode()}"
            
        return "Successfully created and applied database migrations."
        
    except docker.errors.NotFound:
        return "Error: Could not find 'backend' container. Is it running?"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

@mcp.tool()
def restart_backend():
    """
    Restarts the backend FastAPI container.
    """
    client = docker.from_env()
    try:
        backend = client.containers.get("backend")
        backend.restart()
        return "Backend container restarting... Give it 5-10 seconds to come back online."
    except Exception as e:
        return f"Error restarting backend: {str(e)}"

if __name__ == "__main__":
    mcp.run()