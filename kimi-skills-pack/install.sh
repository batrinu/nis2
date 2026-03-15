#!/bin/bash
# Kimi Code Skills Pack — Installer
# Compatible with: Kimi Code CLI, Claude Code, Codex, Gemini CLI, and others

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS=("web-app-builder" "frontend-design" "canvas-design" "systematic-dev" "project-planning" "code-quality" "mcp-builder" "doc-coauthoring" "skill-creator")

echo "╔══════════════════════════════════════════════╗"
echo "║   Kimi Code Skills Pack — Installer          ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Detect target
echo "Where do you want to install?"
echo ""
echo "  1) ~/.config/agents/skills/  (Kimi recommended, cross-tool)"
echo "  2) ~/.kimi/skills/           (Kimi-specific)"
echo "  3) ~/.claude/skills/         (Claude Code, also read by Kimi)"
echo "  4) .agents/skills/           (Current project only)"
echo "  5) Custom path"
echo ""
read -p "Choose [1-5] (default: 1): " choice

case "${choice:-1}" in
  1) TARGET="$HOME/.config/agents/skills" ;;
  2) TARGET="$HOME/.kimi/skills" ;;
  3) TARGET="$HOME/.claude/skills" ;;
  4) TARGET=".agents/skills" ;;
  5) read -p "Enter path: " TARGET ;;
  *) TARGET="$HOME/.config/agents/skills" ;;
esac

echo ""
echo "Installing to: $TARGET"
mkdir -p "$TARGET"

for skill in "${SKILLS[@]}"; do
  if [ -d "$SCRIPT_DIR/$skill" ]; then
    cp -r "$SCRIPT_DIR/$skill" "$TARGET/"
    echo "  ✅ $skill"
  fi
done

echo ""
echo "Done! ${#SKILLS[@]} skills installed."
echo ""
echo "Usage:"
echo "  • Skills auto-trigger based on conversation context"
echo "  • Invoke explicitly: /skill:web-app-builder Build me a ..."
echo "  • Flow mode:         /flow:systematic-dev Plan a feature"
echo ""
echo "If using Kimi Code CLI with --skills-dir:"
echo "  kimi --skills-dir $TARGET"
echo ""
