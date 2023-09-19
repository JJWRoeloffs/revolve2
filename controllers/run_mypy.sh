#!/bin/sh

cd "$(dirname "$0")"
echo "brains:"
mypy -p revolve2
