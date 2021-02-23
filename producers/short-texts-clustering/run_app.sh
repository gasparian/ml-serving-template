#!/bin/sh
gunicorn --chdir ./src app:app \
         --bind=0.0.0.0:5000 \
         --workers=$WORKERS \
         --timeout=120 \
         --worker-class="sync" \
         --graceful-timeout 60 \
         --max-requests 10000 \
      #    --log-level debug \

