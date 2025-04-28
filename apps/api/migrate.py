import os
import subprocess
import sys
import argparse

def run_alembic_command(env, command, extra_args=[]):
    """Ejecuta un comando de Alembic con las variables de entorno configuradas."""
    env_str = f"--env {env}" if env else ""
    cmd_str = f"alembic {command}"
    
    if extra_args:
        cmd_str += f" {' '.join(extra_args)}"
    
    full_cmd = cmd_str
    
    print(f"Running migration in {env} environment: '{full_cmd}'")
    
    # Add database connection verification
    if env == "development":
        import psycopg2
        try:
            conn = psycopg2.connect(
                host=os.environ.get("DEV_DB_HOST", "localhost"),
                port=os.environ.get("DEV_DB_PORT", "5432"),
                dbname=os.environ.get("DEV_DB_NAME", "moneydiary_dev"),
                user=os.environ.get("DEV_DB_USER", "postgres"),
                password=os.environ.get("DEV_DB_PASS", "postgres")
            )
            cursor = conn.cursor()
            cursor.execute("CREATE SCHEMA IF NOT EXISTS app;")
            conn.commit()
            print(f"Database connection verified and schema 'app' created")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Database connection error: {str(e)}")
    
    try:
        # Ejecutar el comando Alembic en un subproceso
        process = subprocess.Popen(
            full_cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),  # Ensure environment variables are passed to subprocess
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error executing migration: Command {full_cmd!r} returned non-zero exit status {process.returncode}.")
            if stderr:
                print(f"STDERR: {stderr.decode()}")
            sys.exit(1)
        
        print(stdout.decode())
        return True
    except Exception as e:
        print(f"Error executing migration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute Alembic migrations with environment configuration")
    parser.add_argument("--env", type=str, default="development", help="Environment (development, testing, production)")
    
    # Parse only the known arguments
    args, unknown = parser.parse_known_args()
    
    # Run the migration command with any remaining arguments
    run_alembic_command(args.env, " ".join(unknown))
