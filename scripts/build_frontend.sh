#!/bin/bash
cd /home/z/my-project/ecoroute/frontend
export NODE_OPTIONS="--max-old-space-size=3072"
/home/z/my-project/ecoroute/frontend/node_modules/.bin/vite build > /tmp/vite-build.log 2>&1
echo "exit=$?"
tail -20 /tmp/vite-build.log
