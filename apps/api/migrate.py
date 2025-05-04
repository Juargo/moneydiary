import os
import subprocess
import sys
import argparse
import shlex
import datetime

def run_alembic_command(env, command, extra_args=[]):
    """Ejecuta un comando de Alembic con las variables de entorno configuradas."""
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(current_dir, "alembic.ini")
    
    # Build the command with proper arguments
    cmd_parts = ["alembic", "-c", config_file]
    
    # Add debug flag if enabled (posición correcta: ANTES del comando)
    if os.environ.get("ALEMBIC_DEBUG") == "1":
        cmd_parts.extend(["-x", "debug=True"])
    
    # Add the command AFTER any global options
    if isinstance(command, str):
        cmd_parts.extend(shlex.split(command))
    else:
        cmd_parts.extend(command)
    
    # Debug information about arguments
    print("\n===== DEBUG: ARGUMENT PROCESSING =====")
    print(f"Original extra_args: {extra_args}")
    print(f"Type: {type(extra_args)}")
    
    # Add any extra arguments with special handling for --message
    if extra_args:
        if isinstance(extra_args, list):
            # Handle --message flag specially to ensure proper quoting
            i = 0
            while i < len(extra_args):
                arg = extra_args[i]
                print(f"Processing arg[{i}]: '{arg}' (type: {type(arg)})")
                
                if arg == '--message' or arg == '-m':
                    print(f"  Found message flag: {arg}")
                    # Add the message flag
                    cmd_parts.append(arg)
                    # If there's a next argument, add it as a quoted string
                    if i + 1 < len(extra_args):
                        message_value = extra_args[i+1]
                        print(f"  Message content: '{message_value}'")
                        quoted_message = f'"{message_value}"'
                        print(f"  Adding quoted message: {quoted_message}")
                        cmd_parts.append(quoted_message)
                        i += 2  # Skip the message value in the next iteration
                        continue
                    else:
                        print("  Warning: --message flag without value")
                else:
                    print(f"  Adding regular arg: {arg}")
                    cmd_parts.append(arg)
                i += 1
        else:
            print(f"Extra args is not a list, using shlex.split: {extra_args}")
            cmd_parts.extend(shlex.split(extra_args))
    
    # Create a readable command string for logging
    full_cmd_str = " ".join(cmd_parts)
    
    print("\n===== DEBUG: COMMAND CONSTRUCTION =====")
    print(f"Final cmd_parts: {cmd_parts}")
    print(f"Command string: '{full_cmd_str}'")
    print("=====================================\n")
    
    print(f"Running migration in {env} environment: '{full_cmd_str}'")
    
    # Add database connection verification
    if env == "dev":
        import psycopg2
        try:
            conn = psycopg2.connect(
                host=os.environ.get("ALEMBIC_DB_HOST"),
                port=os.environ.get("ALEMBIC_DB_PORT"),
                dbname=os.environ.get("ALEMBIC_DB_NAME"),
                user=os.environ.get("ALEMBIC_DB_USER"),
                password=os.environ.get("ALEMBIC_DB_PASS")
            )
            cursor = conn.cursor()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Database connection error: {str(e)}")
    
    # Print debugging information
    print(f"Executing command: {full_cmd_str}")
    print(f"Working directory: {current_dir}")
    print(f"Environment variables:")
    for key in sorted(["ENVIRONMENT", "ALEMBIC_APP_ENV", "ALEMBIC_DB_HOST", "ALEMBIC_DB_PORT", "ALEMBIC_DB_NAME", "ALEMBIC_DB_USER"]):
        if key in os.environ:
            print(f"  {key}={os.environ.get(key)}")
    
    try:
        # Ejecutar el comando Alembic en un subproceso
        process = subprocess.Popen(
            cmd_parts,  # Use the list directly without splitting
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),  # Ensure environment variables are passed to subprocess
            cwd=current_dir,  # Run from the directory containing alembic.ini
        )
        stdout, stderr = process.communicate()
        
        # Always print stdout for debugging
        if stdout:
            stdout_str = stdout.decode()
            print("STDOUT:")
            print(stdout_str)
        
        if process.returncode != 0:
            print(f"Error executing migration: Command '{full_cmd_str}' returned non-zero exit status {process.returncode}.")
            if stderr:
                stderr_str = stderr.decode()
                print("STDERR:")
                print(stderr_str)
                # Print each line of stderr with proper indentation for better readability
                for line in stderr_str.splitlines():
                    print(f"  | {line}")
            sys.exit(1)
        
        # If there's stderr output but command succeeded, still show it as warnings
        if stderr:
            stderr_str = stderr.decode()
            print("WARNINGS from command:")
            for line in stderr_str.splitlines():
                print(f"  | {line}")
        
        return True
    except Exception as e:
        print(f"Error executing migration: {str(e)}")
        # Print more details about the exception
        import traceback
        print("Exception traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute Alembic migrations with environment configuration")
    parser.add_argument("--env", type=str, default="development", help="Environment (development, testing, production)")
    parser.add_argument("--debug", action="store_true", help="Activar modo depuración detallado")

    # Parse only the known arguments
    args, unknown = parser.parse_known_args()
    
    # Configurar el modo debug si está activado
    if args.debug:
        os.environ["ALEMBIC_DEBUG"] = "1"
        debug_log_file = f"alembic_debug_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        print(f"Modo depuración activado. Log: {debug_log_file}")
    
    # Ejecutar el comando una sola vez
    run_alembic_command(args.env, unknown)
