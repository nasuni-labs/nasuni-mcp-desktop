#!/usr/bin/env bash

cd "$(dirname "$0")"
ROOT_DIR="$(pwd)"

if [ -d "nasuni-mcp-server" ]; then
    rm -rf "nasuni-mcp-server"
fi

if [ -f "nasuni-mcp-server.dxt" ]; then
    rm nasuni-mcp-server.dxt
fi

mkdir "nasuni-mcp-server"

cp -r mcp/* nasuni-mcp-server/
cp manifest.json nasuni-mcp-server/
cp icon.png nasuni-mcp-server/
cp .dxtignore nasuni-mcp-server/

cd nasuni-mcp-server

npx @anthropic-ai/dxt pack

cd "$ROOT_DIR"

mv nasuni-mcp-server/nasuni-mcp-server.dxt .

rm -rf nasuni-mcp-server
