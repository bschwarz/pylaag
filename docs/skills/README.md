# pylaag Skills

Reusable AI skills for working with the pylaag library. These follow the [Agent Skills open standard](https://docs.claude.com/en/docs/claude-code/skills) and work with Claude Code, Kiro, and other tools that support the standard.

## Available Skills

| Skill | Description |
|---|---|
| [pylaag-openapi](./pylaag-openapi/SKILL.md) | Creating, reading, and modifying OpenAPI documents with `pylaag-openapi` |
| [pylaag-smithy](./pylaag-smithy/SKILL.md) | Parsing and manipulating AWS Smithy 2.0 models with `pylaag-smithy` |

## Installation

Copy the skill directories you want into your project's `.claude/skills/` folder (Claude Code) or `.kiro/skills/` folder (Kiro):

```bash
# Claude Code
cp -r docs/skills/pylaag-openapi ~/.claude/skills/
cp -r docs/skills/pylaag-smithy ~/.claude/skills/

# Kiro
cp -r docs/skills/pylaag-openapi .kiro/skills/
cp -r docs/skills/pylaag-smithy .kiro/skills/
```

Or copy directly from GitHub into your own project:

```bash
# Claude Code — single skill
curl -o ~/.claude/skills/pylaag-openapi/SKILL.md --create-dirs \
  https://raw.githubusercontent.com/bschwarz/pylaag/main/docs/skills/pylaag-openapi/SKILL.md
```

## Usage

Once installed, skills load automatically when relevant, or invoke them directly:

```
/pylaag-openapi
/pylaag-smithy
```
