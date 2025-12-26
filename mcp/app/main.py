from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from jinja2 import Environment, FileSystemLoader
import os
import re
from typing import List, Literal

from .logging_config import mcp_logger

# --- Configuration ---
app = FastAPI(
    title="Master Control Program (MCP)",
    description="A server for automating code generation and project modifications.",
    version="1.0.0"
)
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
    else:
        mcp_logger.warning(f"Attempted to append to non-existent file: {file_path}")

# --- Pydantic Models for API Requests ---

class FieldDefinition(BaseModel):
    name: str = Field(..., description="The snake_case name of the field.")
    type: Literal["string", "text", "integer", "float", "boolean", "date", "datetime", "uuid"]
    required: bool = True

class CreateResourceRequest(BaseModel):
    resource_name: str = Field(..., description="The singular, snake_case name of the resource (e.g., 'product_item').")
    fields: List[FieldDefinition]

class CreateComponentRequest(BaseModel):
    component_name: str = Field(..., description="The PascalCase name of the component (e.g., 'UserProfile').")
    path: str = Field(..., description="The relative path from 'frontend/src/components' where the file should be created.")
    prompt: str = Field(..., description="A natural language prompt describing the component's purpose.")

# --- MCP Tool Endpoints ---

@app.get("/", tags=["Health Check"])
async def read_root():
    mcp_logger.info("Health check requested.")
    return {"status": "MCP is operational"}

@app.post("/create-resource", tags=["Tools"])
async def create_resource(request: CreateResourceRequest):
    mcp_logger.info(f"Create resource request received: {request.resource_name}")
    # 1. Prepare variables
    ctx = {
        "resource_name_snake": request.resource_name,
        "resource_name_pascal": to_pascal_case(request.resource_name),
        "resource_name_plural_snake": to_plural(request.resource_name),
        "resource_name_plural_pascal": to_pascal_case(to_plural(request.resource_name)),
        "fields": request.fields
    }

    # 2. Define file mappings (template -> output_path)
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

    # 3. Generate files from templates
    for template_name, output_path in files_to_generate.items():
        template = templates_env.get_template(template_name)
        
        # Special handling for models and schemas to inject field definitions
        rendered_content = ""
        if "model.py.j2" in template_name:
            field_lines = [f"    {f.name} = Column({type_to_sqlalchemy(f.type)}, nullable={{not f.required}})" for f in request.fields]
            rendered_content = template.render(ctx).replace("# --- The MCP will add fields here ---", "\n".join(field_lines))
        elif "schema.py.j2" in template_name:
            field_lines = [f"    {f.name}: {type_to_pydantic(f.type)}{' | None' if not f.required else ''}" for f in request.fields]
            rendered_content = template.render(ctx).replace("# --- The MCP will add fields here ---", "\n".join(field_lines))
        else:
            rendered_content = template.render(ctx)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(rendered_content)

    # 4. Modify existing files to include the new resource
    append_to_file(
        "backend/app/models/__init__.py",
        f"\nfrom .{ctx['resource_name_snake']} import {ctx['resource_name_pascal']}"
    )
    append_to_file(
        "backend/app/api/v1/routers.py",
        f"\napi_router.include_router({ctx['resource_name_plural_snake']}.router, prefix='/{ctx['resource_name_plural_snake']}', tags=['{ctx['resource_name_pascal']}'])"
    )
    mcp_logger.info(f"Resource '{request.resource_name}' created successfully. Files: {list(files_to_generate.values())}")
    return {"status": "success", "message": f"Resource '{request.resource_name}' created successfully.", "files_generated": list(files_to_generate.values())}

@app.post("/create-frontend-component", tags=["Tools"])
async def create_frontend_component(request: CreateComponentRequest):
    mcp_logger.info(f"Create frontend component request received: {request.component_name}")
    ctx = {
        "resource_name_pascal": request.component_name,
        "prompt": request.prompt
    }
    template = templates_env.get_template("frontend/component.js.j2")
    rendered_content = template.render(ctx)

    output_path = os.path.join(WORKSPACE_DIR, "frontend/src/components", request.path, f"{request.component_name}.js")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(rendered_content)
    mcp_logger.info(f"Component '{request.component_name}' created at {output_path}")
    return {"status": "success", "message": f"Component '{request.component_name}' created.", "file_path": output_path}