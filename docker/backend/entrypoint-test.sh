#!/bin/bash
# Uso: wait-for-it.sh host:puerto [-t tiempo_espera] [-- comando args]
# -t TIMEOUT: Tiempo máximo de espera (por defecto: 15 segundos)

cmdname=$(basename $0)

# Valores por defecto
TIMEOUT=15
QUIET=0
PROTOCOL=tcp

usage() {
    cat << USAGE >&2
Uso: $cmdname host:puerto [-t tiempo_espera] [-- comando args]
 -q | --quiet                No mostrar mensajes excepto por errores
 -t TIMEOUT | --timeout=TIMEOUT   Segundos a esperar (por defecto: 15)
 -- COMMAND ARGS             Comando a ejecutar después de que el host:puerto esté disponible
USAGE
    exit 1
}

wait_for() {
    if [[ $TIMEOUT -gt 0 ]]; then
        echo "Esperando $TIMEOUT segundos por $HOST:$PORT"
    else
        echo "Esperando indefinidamente por $HOST:$PORT"
    fi
    
    start_ts=$(date +%s)
    while :
    do
        nc -z $HOST $PORT > /dev/null 2>&1
        result=$?
        if [[ $result -eq 0 ]]; then
            end_ts=$(date +%s)
            echo "$HOST:$PORT está disponible después de $((end_ts - start_ts)) segundos"
            break
        fi
        
        if [[ $TIMEOUT -gt 0 ]]; then
            curr_ts=$(date +%s)
            if [[ $((curr_ts - start_ts)) -ge $TIMEOUT ]]; then
                echo "Timeout al esperar por $HOST:$PORT después de $TIMEOUT segundos"
                exit 1
            fi
        fi
        sleep 1
    done
    return 0
}

parse_arguments() {
    local index=0
    while [[ $# -gt 0 ]]
    do
        case "$1" in
            *:* )
                hostport=(${1//:/ })
                HOST=${hostport[0]}
                PORT=${hostport[1]}
                shift 1
                ;;
            -q | --quiet)
                QUIET=1
                shift 1
                ;;
            -t)
                TIMEOUT="$2"
                if [[ $TIMEOUT == "" ]]; then usage; fi
                shift 2
                ;;
            --timeout=*)
                TIMEOUT="${1#*=}"
                shift 1
                ;;
            --)
                shift
                CLI=("$@")
                break
                ;;
            *)
                usage
                ;;
        esac
    done

    if [[ "$HOST" == "" || "$PORT" == "" ]]; then
        usage
    fi
}

parse_arguments "$@"
wait_for

# Ejecutar el comando si se proporciona
if [[ ${#CLI[@]} -gt 0 ]]; then
    exec "${CLI[@]}"
fi