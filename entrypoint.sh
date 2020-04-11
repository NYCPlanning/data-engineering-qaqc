#!/bin/bash
if [ -z "$PORT" ]
then export PORT=5000
else
    echo "port is $PORT"
fi
streamlit run --server.port 5000 index.py