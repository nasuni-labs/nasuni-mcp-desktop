# Nasuni Desktop MCP Solution for SMB shares

## Overview
This project provides a Desktop Model Context Protocol (MCP) Server Solution that lets Claude Desktop safely browse, read, and retrieve files from your Nasuni SMB shares.
It's designed to run on local user's computers to experiment with AI against Nasuni data.

**For additional information and guided training, please visit https://nasuni-customer-academy.workramp.io/training/01999637-8154-7340-ad76-f24dace6a8d5/overview (registration required).**

## Prerequisites

### -**uv** (to run and manage project dependencies)
For installation instructions, see the official docs: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
#### **Mac**
1. Check if you already have Homebrew: `command -v brew && brew --version`  If that prints a version, skip to step 4.	
2. Install Homebrew:
	```
	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	```
3. Add Homebrew to your shell’s PATH (choose one):

	a. Apple Silicon (M1/M2/M3, arm64) — Homebrew prefix is `/opt/homebrew`
	```
	echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
	   eval "$(/opt/homebrew/bin/brew shellenv)"
	```
	b. Intel (x86_64) — Homebrew prefix is `/usr/local`
	```
	echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
	eval "$(/usr/local/bin/brew shellenv)"
	```
4. Install uv:
   ```
   brew update
   brew install uv
   ```
5. Verify the install and that it's on a global path:

   a. Confirm the binary runs: `uv --version`
   
   b. Confirm which executable your shell will use (should be under Homebrew’s bin):
   ```
   command -v uv
   # Expected:
   #   /opt/homebrew/bin/uv   (Apple Silicon)
   #   /usr/local/bin/uv      (Intel)
   ```
   c. Make sure there isn’t a user-local copy shadowing the Homebrew one:
   ```
   which -a uv
   # The first line should be the Homebrew path above.
   # If you see something like ~/.local/bin/uv listed before it, that's a local install shadowing the global one.
   ```
7. Optional - Quick Fixes

	a. uv not found: open a new terminal (to reload PATH) or re-run the shellenv step for your architecture, then: `hash -r   # clear shell command cache`

	b. Wrong uv is picked (e.g., from ~/.local/bin): either remove that path from the front of PATH in your shell profile, or uninstall the local copy, so the Homebrew path wins.
	c. General health checks:
	```
 	brew doctor
	brew info uv
 	```

### -Python
Download: https://www.python.org/downloads/

#### Windows
During installation select the option for *Add python.exe to PATH.*

### -Access to one or more Nasuni SMB shares mounted on your desktop

### -Claude Desktop, or another MCP-compatible AI agent

---

## Configure Your Agent

### Claude Desktop - Install the Extension

1. Download the package *nasuni-mcp-desktop-solution.dxt* from this repository: [DXT package](nasuni-mcp-desktop-solution.dxt)
2. In Claude Desktop, go to Settings → Extensions → Advanced settings → Extension Developer → Install Extension and select the .dxt file.

### Other MCP Clients - Manual Install
If you’re using other tools (e.g., VS Code, Cursor), install and configure the MCP server manually:

1. Extract this repository to a local folder.
2. Configure your MCP server similar to the snippet below (insert into your tool’s config at the appropriate location):
```json
"mcp_config": {
      "command": "uv",
      "args": [
        "run", 
        "--quiet",
        "--directory",
        "MCP_SERVER_PATH",
        "server.py"
      ],
      "env": {
        "FILE_SYSTEM_PATH": "/path/to/mounted/share",
        "MAX_SCAN_ITEMS": 1000,
        "MAX_RETURN_FILE_SIZE": 1048576
      }
    }
```

Where the `MCP_SERVER_PATH` is the absolute path to the folder where this code is installed (the contents of mcp directory from this repo).

#### VS Code

For VS Code, the config file `.vscode/mcp.json` would look like this:
```json
{
	"servers": {
		"my-nasuni-server": {
			"type": "stdio",
			"command": "uv",
			"args": [
				"run",
				"--quiet",
				"--directory",
				"SERVER_PATH",
				"server.py"
			],
			"env": {
				"FILE_SYSTEM_PATH": "/path/to/mounted/share",
				"MAX_SCAN_ITEMS": 1000,
				"MAX_RETURN_FILE_SIZE": 1048576
			}
		}
	},
	"inputs": []
}
```

#### Parameters for manual install

- SERVER_PATH - Required. Absolute path to the folder where this code is installed.
- FILE_SYSTEM_PATH - Required. Path to the mounted SMB share on the local machine. On Windows this is typically `\\server\share` or a mapped drive like `Z:\`.
- MAX_SCAN_ITEMS - Optional. Maximum number of items to scan in a folder. Default: 1000. If a folder contains more than this number of items (files/subfolders), only the first N are returned.
- MAX_RETURN_FILE_SIZE - Optional. Maximum size of any data the server will return to the client. Default: 1,048,576 bytes (≈1 MB). Items larger than this will not be returned.
- MAX_READ_FILE_SIZE - Optional. Maximum size of any file the server will read from the SMB share. Default: 20,048,576 bytes (≈20 MB). Files larger than this will not be read. 
- LOG_DESTINATION - Optional. Where logs are written. Default: empty (no logging). If a valid file path is provided, logs are written to that file; otherwise logs are written to the console.

`MAX_RETURN_FILE_SIZE` vs `MAX_READ_FILE_SIZE` - These limits serve different purposes:
* MAX_READ_FILE_SIZE caps the size of the original file the server will load for processing (e.g., thumbnail generation, text extraction).
* MAX_RETURN_FILE_SIZE caps the size of the output the server will send back after processing (e.g., a thumbnail or extracted text).

Example
cat.png is 2,048 KB. An AI agent calls image_file_contents with thumb_width=512 (generate a 512-px-wide thumbnail).
* If `MAX_READ_FILE_SIZE` = 1,024 KB, the original file is too large to read → error.
* If `MAX_READ_FILE_SIZE` = 4,096 KB, the server reads the file, creates the thumbnail, and then compares the thumbnail’s size to `MAX_RETURN_FILE_SIZE`:
	* If the thumbnail size ≤ `MAX_RETURN_FILE_SIZE` → the thumbnail is returned.
	* If the thumbnail size > `MAX_RETURN_FILE_SIZE` → error.

---

## Supported Tools

All paths are relative to the configured root (`FILE_SYSTEM_PATH`) and use / as the separator.

1. **folder_contents(path: str = "") -> FolderContents**
	- **Arguments:** `path` (str, optional)
	- **Description:** Returns a list of files and subfolders within path. If path is empty, returns the root folder contents.

2. **file_metadata(path: str) -> FileMetadata**
	- **Arguments:** `path` (str, required)
	- **Description:** Returns file metadata (e.g., size, type, whether it’s readable as an image, and whether text can be extracted).

3. **file_contents(path: str) -> str**
	- **Arguments:** `path` (str, required)
	- **Description:** Downloads the file and returns its contents as a string. Best for text or text-based formats. Binary files may yield unreadable output; prefer `file_contents_base64()` for binary data or `image_file_contents()` for images.

4. **file_contents_base64(path: str) -> str**
	- **Arguments:** `path` (str, required)
	- **Description:** Downloads the file and returns its contents as a Base64-encoded string. Recommended for binary files.

5. **image_file_contents(path: str, thumb_width: int = 0) -> Image**
	- **Arguments:** `path` (str, required), `thumb_width` (int, optional)
	- **Description:** Downloads a PNG or JPEG image and returns an Image object. If `thumb_width > 0`, returns a thumbnail resized to that width while preserving aspect ratio.

6. **file_file_contents_as_text(path: str) -> str**
	- **Arguments:** `path` (str, required)
	- **Description:** Retrieves a file and returns extracted text when supported (PDF, DOCX). For other types, returns the raw content as a string (same behavior as `file_contents()`).



---

## Security Disclaimer

This software is provided as is and carries inherent security risks. Large Language Models (LLMs) and related systems cannot currently be fully secured against malicious inputs, which may lead to unintended behavior or data exposure. By using this MCP integration, you assume all responsibility for associated risks and agree that the authors accept no liability for any security incidents or consequences.


## Nasuni Labs Disclaimer

Nasuni Labs projects are community-supported and maintained within this repository. They are provided as-is, without guarantees or formal Nasuni support. Use at your own discretion.
