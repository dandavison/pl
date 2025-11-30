#!/bin/bash
set -e

# Debug output to stderr
echo "Starting ytmusic-mcp wrapper..." >&2
echo "PATH: $PATH" >&2
echo "HOME: $HOME" >&2
echo "Git version: $(git --version 2>&1)" >&2

# Run without verbose flag and keep stderr separate
exec uvx --from git+https://github.com/dandavison/pl ytmusic-mcp
