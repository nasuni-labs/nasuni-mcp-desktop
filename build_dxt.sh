#!/usr/bin/env bash

cd "$(dirname "$0")"
ROOT_DIR="$(pwd)"
TOOL_NAME="nasuni-mcp-desktop-solution"

if [ -d "$TOOL_NAME" ]; then
    rm -rf "$TOOL_NAME"
fi

if [ -f "$TOOL_NAME.dxt" ]; then
    rm "$TOOL_NAME.dxt"
fi

mkdir "$TOOL_NAME"

cp -r mcp/* "$TOOL_NAME/"
cp manifest.json "$TOOL_NAME/"
cp icon.png "$TOOL_NAME/"
cp .dxtignore "$TOOL_NAME/"

cd "$TOOL_NAME"

npx @anthropic-ai/dxt pack

cd "$ROOT_DIR"

mv "$TOOL_NAME/$TOOL_NAME.dxt" .

rm -rf "$TOOL_NAME"
