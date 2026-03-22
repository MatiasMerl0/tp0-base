#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Uso: $0 <archivo_salida> <cantidad_clientes>"
    exit 1
fi

python3 generate-compose.py "$1" "$2"
