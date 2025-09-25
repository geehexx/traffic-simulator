# 📁 Prompt Directory Structure Clarification

## 🎯 The Issue

You were absolutely right to question why we have two prompts directories! This was a configuration mistake on my part.

## ✅ **Correct Structure (Now Fixed)**

### **Main Prompts Directory: `/prompts/`**
- **Location**: `/home/gxx/projects/traffic-simulator/prompts/`
- **Purpose**: Main production prompts directory
- **Contents**:
  - Production prompt files (`generate_docs_v2_2_0.json`, etc.)
  - Prompt manifest (`manifest.json`) - **ONLY FILE USED BY MCP SERVER**
  - **Prompt Wizard files** (moved here)

### **MCP Server Configuration**
- **File**: `mcp/fastmcp_production_server.py`
- **Configuration**: `PROMPTS_DIR = Path("../prompts")` (points to main directory)
- **Working Directory**: `/mcp/` (so `../prompts` resolves to `/prompts/`)

## 🔧 **What Was Wrong**

1. **I mistakenly created** `/mcp/prompts/` when building the Prompt Wizard
2. **The MCP server was using** the wrong directory (`/mcp/prompts/` instead of `/prompts/`)
3. **This caused confusion** about which directory was the "main" one

## ✅ **What I Fixed**

1. **Moved all Prompt Wizard files** from `/mcp/prompts/` to `/prompts/`
2. **Updated MCP server configuration** to use `Path("../prompts")` (main directory)
3. **Removed the duplicate** `/mcp/prompts/` directory
4. **Updated documentation** to reflect correct paths

## 🎯 **Current Structure**

```
/home/gxx/projects/traffic-simulator/
├── prompts/                          # ← MAIN PROMPTS DIRECTORY
│   ├── generate_docs_v2_2_0.json     # Production prompts
│   ├── manifest.json                 # Prompt manifest (ONLY FILE USED BY MCP)
│   ├── prompt-wizard.json            # Prompt Wizard files
│   ├── prompt-wizard-advanced.json   # (moved here)
│   └── prompt-wizard-scenarios.json # (moved here)
└── mcp/
    └── fastmcp_production_server.py  # Points to ../prompts
```

## 🚀 **Result**

- **Single source of truth**: `/prompts/` is the only prompts directory
- **MCP server uses correct directory**: Points to main `/prompts/` directory
- **All Prompt Wizard files**: Now in the correct location
- **No more confusion**: Clear, single directory structure

## 📋 **Verification**

The MCP server now correctly uses the main `/prompts/` directory, and all Prompt Wizard files are in the right place. The system is properly configured and ready to use!

---

**Thank you for catching this! The directory structure is now correct and consolidated.** 🎯
