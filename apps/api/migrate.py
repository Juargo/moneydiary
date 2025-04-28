import os
import sys
import argparse
import subprocess
import shlex

def run_migration(env, command):
    """Ejecuta un comando de alembic en el ambiente especificado."""
    os.environ["APP_ENV"] = env
    print(f"Running migration in {env} environment: 'alembic {command}'")
    
    # Convertir el comando en lista de argumentos
    cmd_parts = ["alembic"] + shlex.split(command)
    
    try:
        result = subprocess.run(cmd_parts, check=True, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        print(f"Migration command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing migration: {e}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ejecutar migraciones de Alembic")
    parser.add_argument("--env", choices=["development", "testing", "production"], 
                        default="development", help="Ambiente de ejecución")
    parser.add_argument("command", choices=["upgrade", "downgrade", "revision", "current", "history", "merge"],
                        help="Comando de Alembic")
    parser.add_argument("--message", help="Mensaje para el comando 'revision'")
    parser.add_argument("--rev", help="Revisión para comandos 'upgrade' y 'downgrade'")
    parser.add_argument("--autogenerate", action="store_true", help="Usar --autogenerate con revision")
    
    args = parser.parse_args()
    
    alembic_cmd = args.command
    if args.command == "revision":
        if args.message:
            alembic_cmd += f" --message '{args.message}'"
        if args.autogenerate:
            alembic_cmd += " --autogenerate"
    elif args.command in ["upgrade", "downgrade"]:
        if args.rev:
            alembic_cmd += f" {args.rev}"
        else:
            alembic_cmd += " head" if args.command == "upgrade" else " -1"
    
    run_migration(args.env, alembic_cmd)