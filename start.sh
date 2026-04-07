#!/bin/bash
# Ensure data directories exist (volume mount may be empty)
mkdir -p ${DATA_DIR:-data}/{conversations,strategies,memory,voice,evals}

# Start API server on port 8000 (internal)
uvicorn src.api:app --host 0.0.0.0 --port 8000 &

# Start Streamlit dashboard on Railway's PORT (public-facing)
API_URL=http://localhost:8000 streamlit run src/dashboard.py \
  --server.port ${PORT:-8501} \
  --server.address 0.0.0.0 \
  --server.headless true
