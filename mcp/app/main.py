import os
import subprocess
import typer
from jinja2 import Environment, FileSystemLoader
from typing import List, Literal
from typing_extensions import Annotated

# --- Typer App Initialization ---
app = typer.Typer(help="Master Control Program for project scaffolding and management.")

# --- Configuration ---
# Assuming the script is run from within the container, paths are set accordingly.
TEMPLATES_DIR = "/app/templates"
WORKSPACE_DIR = "/workspace"
templates_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

# --- Helper Functions ---
def to_pascal_case(snake_case: str) -> str:
    """Converts snake_case_string to PascalCaseString."""
    return "".join(word.capitalize() for word in snake_case.split('_'))

def to_plural(snake_case: str) -> str:
    """Converts a singular snake_case string to its plural form."""
    if snake_case.endswith('y'):
        return snake_case[:-1] + 'ies'
    if snake_case.endswith('s'):
        return snake_case + 'es'
    return snake_case + 's'

def type_to_sqlalchemy(field_type: str) -> str:
    """Maps a CLI-friendly type to a SQLAlchemy type."""
    mapping = {
        "string": "String", "text": "Text", "integer": "Integer",
        "float": "Float", "boolean": "Boolean", "date": "Date",
        "datetime": "DateTime", "uuid": "Uuid"
    }
    return mapping.get(field_type, "String")

def type_to_pydantic(field_type: str) -> str:
    """Maps a CLI-friendly type to a Pydantic/Python type."""
    mapping = {
        "string": "str", "text": "str", "integer": "int",
        "float": "float", "boolean": "bool", "date": "date",
        "datetime": "datetime", "uuid": "UUID"
    }
    return mapping.get(field_type, "str")
    
class Field:
    """Helper class to parse and hold field definition."""
    def __init__(self, definition: str):
        try:
            parts = definition.split(':')
            if len(parts) != 3:
                raise ValueError("Field definition must be in 'name:type:required' format.")
            self.name = parts[0].strip()
            self.type = parts[1].strip()
            self.required = parts[2].strip().lower() in ['true', '1', 't', 'y', 'yes']
            if self.type not in ["string", "text", "integer", "float", "boolean", "date", "datetime", "uuid"]:
                 raise ValueError(f"Invalid field type: {self.type}")
        except Exception as e:
            typer.echo(f"Error parsing field definition '{definition}': {e}")
            raise typer.Exit(code=1)

# --- CLI Commands ---

@app.command("create-resource")
def create_resource(
    resource_name: Annotated[str, typer.Argument(help="The singular snake_case name of the resource (e.g., 'product_item').")],
    fields: Annotated[List[str], typer.Argument(help="List of field definitions in 'name:type:required' format (e.g., 'title:string:true' 'content:text:false').")]
):
    """
    Scaffolds a new resource: backend models, schemas, CRUD, endpoints, and frontend API handlers.
    """
    typer.echo(f"Creating resource: {resource_name}")

    parsed_fields = [Field(f) for f in fields]

    ctx = {
        "resource_name_snake": resource_name,
        "resource_name_pascal": to_pascal_case(resource_name),
        "resource_name_plural_snake": to_plural(resource_name),
        "resource_name_plural_pascal": to_pascal_case(to_plural(resource_name)),
        "fields": parsed_fields,
        "type_to_sqlalchemy": type_to_sqlalchemy,
        "type_to_pydantic": type_to_pydantic
    }

    base_paths = {
        "backend": os.path.join(WORKSPACE_DIR, "backend/app"),
        "frontend": os.path.join(WORKSPACE_DIR, "frontend/src")
    }

    files_to_generate = {
        # Backend
        "backend/model.py.j2": os.path.join(base_paths["backend"], f"models/{ctx['resource_name_snake']}.py"),
        "backend/schema.py.j2": os.path.join(base_paths["backend"], f"db/schemas/{ctx['resource_name_snake']}.py"),
        "backend/crud.py.j2": os.path.join(base_paths["backend"], f"crud/crud_{ctx['resource_name_snake']}.py"),
        "backend/endpoint.py.j2": os.path.join(base_paths["backend"], f"api/v1/endpoints/{ctx['resource_name_plural_snake']}.py"),
        # Frontend API Handlers
        "frontend/api_index.js.j2": os.path.join(base_paths["frontend"], f"pages/api/{ctx['resource_name_plural_snake']}/index.js"),
        "frontend/api_id.js.j2": os.path.join(base_paths["frontend"], f"pages/api/{ctx['resource_name_plural_snake']}/[{ctx['resource_name_snake']}Id].js"),
    }
    
    generated_list = []
    for template_name, output_path in files_to_generate.items():
        template = templates_env.get_template(template_name)
        rendered_content = template.render(ctx)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(rendered_content)
        generated_list.append(output_path.replace(WORKSPACE_DIR, ""))

    typer.echo("Generated files:")
    for path in generated_list:
        typer.echo(f"- {path}")

    # --- Modify backend router ---
    try:
        routers_file_path = os.path.join(base_paths["backend"], "api/v1/routers.py")
        with open(routers_file_path, "r+") as f:
            content = f.read()
            plural_snake = ctx['resource_name_plural_snake']
            pascal = ctx['resource_name_pascal']
            
            new_import = f"from app.api.v1.endpoints import {plural_snake}"
            if new_import not in content:
                content = content.replace("from app.api.v1.endpoints import users", f"from app.api.v1.endpoints import users\n{new_import}")

            new_router = f"api_router.include_router({plural_snake}.router, prefix='/{plural_snake}', tags=['{pascal}'])"
            if new_router not in content:
                content += f"\n{new_router}"
            
            f.seek(0)
            f.write(content)
            f.truncate()
        typer.echo("Updated backend router.")
    except Exception as e:
        typer.echo(f"Error modifying backend router: {e}", err=True)

    # --- Modify models/__init__.py to allow Alembic autodiscovery ---
    try:
        models_init_path = os.path.join(base_paths["backend"], "models/__init__.py")
        with open(models_init_path, "a") as f:
            f.write(f"\nfrom .{ctx['resource_name_snake']} import {ctx['resource_name_pascal']}")
        typer.echo("Updated models package for autodiscovery.")
    except Exception as e:
        typer.echo(f"Error modifying models package: {e}", err=True)
    
    typer.secho(f"Successfully created resource '{resource_name}'.", fg=typer.colors.GREEN)

@app.command("add-middleware-route")
def add_middleware_route(
    route_path: Annotated[str, typer.Argument(help="The path to add (e.g., '/api/my_data').")],
    route_type: Annotated[Literal["auth_required", "admin"], typer.Argument(help="The type of route protection ('auth_required' or 'admin').")]
):
    """
    Adds a new route path to the AUTH_REQUIRED_ROUTES or ADMIN_ROUTES array in frontend/src/middleware.js.
    """
    middleware_file_path = os.path.join(WORKSPACE_DIR, "frontend/src/middleware.js")
    target_array = "AUTH_REQUIRED_ROUTES" if route_type == "auth_required" else "ADMIN_ROUTES"
    
    try:
        with open(middleware_file_path, "r+") as f:
            lines = f.readlines()
            # Find the line where the target array is defined
            for i, line in enumerate(lines):
                if f"const {target_array} = [" in line:
                    # Find the closing bracket of the array
                    for j in range(i, len(lines)):
                        if "]" in lines[j]:
                            # Insert the new route before the closing bracket
                            lines.insert(j, f'  "{route_path}",\n')
                            break
                    else:
                        raise ValueError(f"Could not find closing bracket for {target_array}")
                    break
            else:
                raise ValueError(f"Could not find array definition for {target_array}")

            f.seek(0)
            f.writelines(lines)
            f.truncate()
        typer.secho(f"Added route '{route_path}' to {target_array}.", fg=typer.colors.GREEN)
    except Exception as e:
        typer.echo(f"Error updating middleware file: {e}", err=True)
        raise typer.Exit(code=1)

@app.command("create-frontend-component")
def create_frontend_component(
    component_name: Annotated[str, typer.Argument(help="PascalCase name for the component (e.g., 'UserProfile').")],
    path: Annotated[str, typer.Argument(help="Relative path from frontend/src/components (e.g., 'users').")],
    prompt: Annotated[str, typer.Option(help="A prompt describing what the component should do.")] = "This is a new component."
):
    """
    Creates a new React frontend component from a template.
    """
    ctx = {"component_name": component_name, "prompt": prompt}
    template = templates_env.get_template("frontend/component.js.j2")
    rendered_content = template.render(ctx)

    output_dir = os.path.join(WORKSPACE_DIR, "frontend/src/components", path)
    output_path = os.path.join(output_dir, f"{component_name}.js")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(rendered_content)
        typer.secho(f"Component '{component_name}' created at {output_path.replace(WORKSPACE_DIR, '')}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.echo(f"Error creating component: {e}", err=True)
        raise typer.Exit(code=1)

def _run_docker_compose_command(service: str, command: List[str]):
    base_command = ["docker-compose", "-f", os.path.join(WORKSPACE_DIR, "docker-compose.yml"), "exec", service]
    full_command = base_command + command
    typer.echo(f"Running command: {" ".join(full_command)}")
    try:
        result = subprocess.run(full_command, capture_output=True, text=True, check=True)
        typer.echo(result.stdout)
        if result.stderr:
            typer.echo("Stderr:", err=True)
            typer.echo(result.stderr, err=True)
        return True
    except FileNotFoundError:
        typer.echo("Error: 'docker-compose' command not found. Is Docker installed and in your PATH?", err=True)
        return False
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error executing command: {" ".join(full_command)}", err=True)
        typer.echo(e.stdout)
        typer.echo(e.stderr, err=True)
        return False

@app.command("apply-migrations")
def apply_migrations(
    message: Annotated[str, typer.Option(help="Message for the Alembic revision.")] = "New migration"
):
    """
    Generates and applies database migrations inside the backend container.
    """
    typer.echo("Generating Alembic revision...")
    success = _run_docker_compose_command("backend", ["alembic", "revision", "--autogenerate", "-m", message])
    if not success:
        typer.echo("Failed to generate revision.", err=True)
        raise typer.Exit(code=1)

    typer.echo("Applying migrations...")
    success = _run_docker_compose_command("backend", ["alembic", "upgrade", "head"])
    if not success:
        typer.echo("Failed to apply migrations.", err=True)
        raise typer.Exit(code=1)
    
    typer.secho("Database migrations applied successfully.", fg=typer.colors.GREEN)

@app.command("restart-backend")
def restart_backend():
    """
    Restarts the backend FastAPI container using docker-compose.
    """
    command = ["docker-compose", "-f", os.path.join(WORKSPACE_DIR, "docker-compose.yml"), "restart", "backend"]
    typer.echo("Restarting backend container...")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        typer.secho("Backend container restarted successfully.", fg=typer.colors.GREEN)
    except FileNotFoundError:
        typer.echo("Error: 'docker-compose' command not found. Is Docker installed and in your PATH?", err=True)
        raise typer.Exit(code=1)
    except subprocess.CalledProcessError as e:
        typer.echo("Error restarting backend:", err=True)
        typer.echo(e.stdout)
        typer.echo(e.stderr, err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()