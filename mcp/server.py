"""MCP Server for Nasuni SMB"""
import base64
import os
import sys
from mcp.server.fastmcp import FastMCP, Image
from app.config import Config
from app import init_logger, get_file_system_client
from app.utils import (
    extract_text_from_file, 
    get_image_thumb,
    verify_length_is_not_too_large_to_return
)
from app.file_system import FolderContents, FileMetadata, SizeLimitKind

config = Config()
log = init_logger(config)

file_system_client = get_file_system_client(config, log)

mcp = FastMCP("Nasuni File Storage Server")

@mcp.tool()
def folder_contents(path: str = "") -> FolderContents:
    """
    Returns list of files and sub folders by the folder from SMB share.
    Accepts path to the folder. If the path is empty, it returns the root folder contents.
    The path is relative to the root folder. Names are delimited with '/'.
    """

    return file_system_client.folder_contents(path)

@mcp.tool()
def file_metadata(path: str) -> FileMetadata:
    """
    Returns metadata for a file from SMB share.
    This represents a file size and detects if a file can be treated 
    as image or a text can be extracted from the file.
    The path is relative to the root folder. Names are delimited with '/'.
    """
    return file_system_client.get_metadata(path)


@mcp.tool()
def file_contents(path: str) -> str:
    """
    Download file from the SMB share. Returns a file contents converted to a string.
    Files with binary contents can have unexpected results.
    This method works the best for text or hypertext files.
    If a file is binary, or contains non plain text content, 
    it is recommended to use file_contents_base64() method, which works better for binary files. 
    Or use image_file_contents() method for images of supported formats.
    The path is relative to the root folder. Names are delimited with '/'.
    """
    return file_system_client.get_file_content_as_string(path)

@mcp.tool()
def file_contents_base64(path: str) -> str:
    """
    Download file from the SMB share. Returns a file contents encoded as base64.
    This works the best with binary files.
    The path is relative to the root folder. Names are delimited with '/'.
    """
    contents = file_system_client.get_file_content(path)
    encoded_contents = base64.b64encode(contents).decode("utf-8")
    return encoded_contents
    
@mcp.tool()
def image_file_contents(path: str, thumb_width: int = 0) -> Image:
    """
    Download image file from the SMB share. Returns an Image object.
    This works only for image files of types png and jpeg.
    The path is relative to the root folder. Names are delimited with '/'.
    The image can be resized by specifying the thumb_width parameter. If thumb_width is greater than 0,
    the image will be resized to the specified width while maintaining the aspect ratio.
    """

    # This will throw an exception if the format is not supported
    image_format = file_system_client.get_image_file_format(path)

    # Read the file depending on the limit. If we need thumb then we can read bigger file
    limit_kind = SizeLimitKind.READ if thumb_width > 0 else SizeLimitKind.RETURN

    image_data = file_system_client.get_file_content(path, limit_kind)

    if thumb_width > 0:
        # Resize the image to the specified thumbnail width
        image_data = get_image_thumb(image_data, thumb_width, image_format)
        # final check of the length
        verify_length_is_not_too_large_to_return(len(image_data), config)

    return Image(data=image_data, format=image_format)

@mcp.tool()
def file_file_contents_as_text(path: str) -> str:
    """
    Retrieve file from the SMB share and extract text data from it.
    It is supported for pdf and docx files.
    For other files it will return the file content as a string same as file_contents() method.
    The path is relative to the root folder. Names are delimited with '/'.
    """

    text = extract_text_from_file(path, 
                                  file_system_client.get_file_content(path, SizeLimitKind.READ)
                                  )
    
    verify_length_is_not_too_large_to_return(len(text), config)
    
    return text

if __name__ == "__main__":
    mcp.run()
