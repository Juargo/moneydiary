#!/usr/bin/env python3
"""
Script para verificar conflictos de dependencias en Python antes de construir la imagen Docker.
"""

import os
import sys
import subprocess
from packaging.requirements import Requirement
from packaging.version import Version, parse
from collections import defaultdict

def parse_requirements_file(file_path):
    """Parsea un archivo requirements.txt y devuelve un diccionario de paquete->versión."""
    requirements = {}
    
    if not os.path.exists(file_path):
        print(f"El archivo {file_path} no existe.")
        return requirements
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    req = Requirement(line)
                    package_name = req.name.lower()
                    if req.specifier:
                        requirements[package_name] = str(req.specifier)
                    else:
                        requirements[package_name] = "Any version"
                except Exception as e:
                    print(f"No se pudo analizar la línea: {line}, Error: {e}")
    
    return requirements

def check_conflicts(requirements):
    """Verifica si hay conflictos en las dependencias."""
    packages = defaultdict(list)
    
    for pkg, version in requirements.items():
        packages[pkg].append(version)
    
    conflicts = {pkg: versions for pkg, versions in packages.items() if len(versions) > 1}
    
    return conflicts

def main():
    """Función principal."""
    requirements_file = "../backend/requirements.txt"
    
    print(f"Analizando dependencias en {requirements_file}...")
    requirements = parse_requirements_file(requirements_file)
    
    print("\nDependencias encontradas:")
    for pkg, version in requirements.items():
        print(f"  {pkg}: {version}")
    
    # Agregar las dependencias que queremos instalar manualmente
    manual_deps = {
        'pydantic': '==1.10.7',
        'python-dateutil': '==2.8.2',
        'asgiref': '==3.7.2',
        'mysqlclient': 'latest'
    }
    
    print("\nDependencias manuales a instalar:")
    for pkg, version in manual_deps.items():
        print(f"  {pkg}: {version}")
        if pkg in requirements:
            print(f"  ⚠️ CONFLICTO: {pkg} ya está en requirements.txt con versión {requirements[pkg]}")
    
    all_deps = {**requirements, **manual_deps}
    conflicts = check_conflicts(all_deps)
    
    if conflicts:
        print("\n⚠️ Se encontraron posibles conflictos:")
        for pkg, versions in conflicts.items():
            print(f"  {pkg}: {', '.join(versions)}")
        
        print("\nSugerencias para resolver conflictos:")
        print("1. Eliminar la especificación de versión en requirements.txt")
        print("2. Usar la misma versión en todas las dependencias")
        print("3. Usar --no-deps para instalar versiones específicas")
        
        return 1
    else:
        print("\n✅ No se encontraron conflictos en las dependencias.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
