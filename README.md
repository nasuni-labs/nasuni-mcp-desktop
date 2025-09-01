# MCP Server for SMB share with STDIO

## Install

This tool requires the `uv` tool installed. It helps to install and manage the project dependencies. FInd how to install `uv` if you do not have it yet [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

### Install DXT file in Claude Desktop

There is the file nasuni-mcp-desktop.dxt in this repo. Download it and install it in Claude Desktop in the Extensions view. [Get DXT package](nasuni-mcp-server.dxt)

### Manual install

DXT package works only with Claude Desktop. For other AI Agent tools (VS Code, Cursor or any custom AI agents supporting MCP) you need to install and configure the MCP server manually.

Untar this repository somewhere.

Configure the MCP server similar to this:

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

## Using with VSCode

The config file `.vscode/mcp.json` would look like this:

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

## Config for manual install

- SERVER_PATH - it is the absolute path to the folder where this code is installed.
- FILE_SYSTEM_PATH - The path to the mounted SMB share on the local file system. Required. It is the local file system absolute path. On Windows, this is typically in the form of `\\server\share` or `Z:\`.
- MAX_SCAN_ITEMS - The maximum number of items to scan in the SMB share. Optional. Default is 1000. If a folder has more than 1000 items (files/subfolders), only the first 1000 will be returned.
- MAX_RETURN_FILE_SIZE - The maximum size of a file to return from the SMB share. Optional. Default is 1048576 (1MB). Files bigger this size will not be read by this tool.
- MAX_READ_FILE_SIZE - The maximum size of a file to read from the SMB share. Optional. Default is 20048576 (20MB). Files bigger this size will not be read by this tool. 
- LOG_DESTINATION - The destination for log output. Optional. Default is empty meaning no logging. If a valid file path is provided then logs will be output there.

`MAX_RETURN_FILE_SIZE` vs `MAX_READ_FILE_SIZE`: The difference is visible and affects only for tools that can convert a file contents (image_file_contents and file_file_contents_as_text). MAX_READ_FILE_SIZE allows to control maximum size of the original file. And `MAX_RETURN_FILE_SIZE` controls the maximum size of the file that can be returned by the server after processing.

Example: cat.png has the size 2048KB. AI agent uses the tool `image_file_contents` with the argument thumb_width=512 (the image must be converted to a thumbnail with 512 pixels width). 
- If `MAX_READ_FILE_SIZE` is set to 1024KB then the original file can not be read. Error will be returned.
- If `MAX_READ_FILE_SIZE` is set to 4096KB then the original file can be read. Then the server will create the thumbnail and compare the thumbnail size to `MAX_RETURN_FILE_SIZE`. If the thumbnail size is less than `MAX_RETURN_FILE_SIZE`, the thumbnail will be returned. If the thumbnail size is greater than `MAX_RETURN_FILE_SIZE`, an error will be returned.

## Supported tools


The following tools are available in this server:

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
