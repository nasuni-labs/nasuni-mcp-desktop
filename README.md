# Nasuni Desktop MCP Solution for SMB shares with STDIO

## Overview
This project provides a Desktop Model Context Protocol (MCP) Server Solution that lets AI agents (such as Claude Desktop and other MCP-compatible tools) safely browse, read, and retrieve files from your Nasuni SMB shares via STDIO.
It’s designed for use by Nasuni admins or power users in the context of their local computers to experiment with AI against Nasuni data.

## Prerequisites

* `uv` is required to run and manage project dependencies.
	* For installation instructions, see the official docs: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
* Python must be installed. On Windows, during installation check *Add python.exe to PATH.*
	* Download: https://www.python.org/downloads/
* Access to one or more Nasuni SMB shares mounted on your desktop
* Claude Desktop, or another MCP-compatible AI agent

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
	- **Description:** Returns list of files and sub folders by the folder from SMB share. Accepts path to the folder. If the path is empty, it returns the root folder contents. The path is relative to the root folder. Names are delimited with '/'.

2. **file_metadata(path: str) -> FileMetadata**
	- **Arguments:** `path` (str)
	- **Description:** Returns metadata for a file from SMB share. This represents a file size and detects if a file can be treated as image or a text can be extracted from the file. The path is relative to the root folder. Names are delimited with '/'.

3. **file_contents(path: str) -> str**
	- **Arguments:** `path` (str)
	- **Description:** Download file from the SMB share. Returns a file contents converted to a string. Files with binary contents can have unexpected results. This method works the best for text or hypertext files. If a file is binary, or contains non plain text content, it is recommended to use file_contents_base64() method, which works better for binary files. Or use image_file_contents() method for images of supported formats. The path is relative to the root folder. Names are delimited with '/'.

4. **file_contents_base64(path: str) -> str**
	- **Arguments:** `path` (str)
	- **Description:** Download file from the SMB share. Returns a file contents encoded as base64. This works the best with binary files. The path is relative to the root folder. Names are delimited with '/'.

5. **image_file_contents(path: str, thumb_width: int = 0) -> Image**
	- **Arguments:** `path` (str), `thumb_width` (int, optional)
	- **Description:** Download image file from the SMB share. Returns an Image object. This works only for image files of types png and jpeg. The path is relative to the root folder. Names are delimited with '/'. The image can be resized by specifying the thumb_width parameter. If thumb_width is greater than 0, the image will be resized to the specified width while maintaining the aspect ratio.

6. **file_file_contents_as_text(path: str) -> str**
	- **Arguments:** `path` (str)
	- **Description:** Retrieve file from the SMB share and extract text data from it. It is supported for pdf and docx files. For other files it will return the file content as a string same as file_contents() method. The path is relative to the root folder. Names are delimited with '/'.
