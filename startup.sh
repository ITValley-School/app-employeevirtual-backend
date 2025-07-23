#!/bin/bash

echo "🟢 Iniciando aplicação com uvicorn..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000
