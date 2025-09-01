"""File system utilities."""
from html import parser
from enum import Enum
import logging
import os
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

from .config import Config
from .models import FolderContents, FileSystemItem, FolderItem, FileItem, FileMetadata

class SizeLimitKind(Enum):
    """Enum for file size limits kinds"""
    READ = "read"
    RETURN = "return"
    NONE = "none"

class FileSystem:
    """
    Represents the file system and provides methods to interact with it.
    """

    def __init__(self, config: Config, log: logging.Logger | None = None):
        self.config = config
        if log is not None:
            self.log = log
        else:
            self.log = logging.getLogger("null")
            self.log.addHandler(logging.NullHandler())

    def folder_contents(self, relative_path, scan_limit: int | None = None) -> FolderContents:
        """
        Get the contents of a folder.
        """

        if relative_path == "/" or relative_path == "\\":
            relative_path = ""

        scan_first_items = self.config.max_scan_items if scan_limit is None else scan_limit
        folder_path = self._build_path(relative_path)

        self._require_path_is_in_excluded_folder(folder_path)

        folder_name = os.path.basename(relative_path)
        if relative_path.endswith("/"):
            folder_name = os.path.basename(os.path.dirname(relative_path))

        contents = FolderContents(folder=FolderItem(name=folder_name, path=relative_path))

        items : list[FileSystemItem] = []
        for entry in os.scandir(folder_path):
            item_path = relative_path

            if relative_path and not relative_path.endswith("/"):
                item_path += "/"

            item_path += entry.name

            if entry.is_dir():
                # Ensure this folder is not some excluded folder or inside one
                absolute_item_path = self._build_path(item_path)
                if self._check_path_is_in_excluded_folder(absolute_item_path):
                    continue
                item = FolderItem(name=entry.name, path=item_path)
            else:
                item = FileItem(
                    name=entry.name,
                    path=item_path,
                    size=entry.stat().st_size)
                if self.config.max_return_file_size:
                    item.define_if_is_too_large(self.config.max_return_file_size)

            items.append(FileSystemItem(item=item))

            if scan_first_items and len(items) >= scan_first_items:
                break

        contents.load_contents(items)
        return contents
    
    def get_metadata(self, path: str) -> FileMetadata:
        """
        Get the metadata of a file.
        """

        full_path = self._build_path(path)

        self._require_path_is_in_excluded_folder(full_path)
        
        stat = os.stat(full_path)

        if os.path.isdir(full_path):
            raise ValueError("Path is a directory")

        item = FileItem(
            name=os.path.basename(path),
            path=path,
            size=stat.st_size
        )
        if self.config.max_return_file_size:
            item.define_if_is_too_large(self.config.max_return_file_size)

        metadata = FileMetadata(file_item=item, metadata={})

        parser = createParser(full_path)
        if not parser:
            raise SystemExit(f"Unable to parse file: {path}")

        extracted_metadata = extractMetadata(parser)
        if extracted_metadata:
            for item in extracted_metadata:
                if item.values:  # some items may be empty
                    # many items can have multiple values; print them all
                    vals = [v.value for v in item.values]
                    metadata[item.key] = vals if len(vals) > 1 else vals[0]

        return metadata

    def get_file_content(self, path: str, size_limit_kind: SizeLimitKind = SizeLimitKind.RETURN) -> bytes:
        """
        Get the content of a file as bytes.
        """
        full_path = self._build_path(path)
        
        self._check_file_size_is_not_too_large(full_path, size_limit_kind)
        
        self._require_path_is_in_excluded_folder(full_path)

        with open(full_path, "rb") as f:
            return f.read()

    def get_file_content_as_string(self, path: str, size_limit_kind: SizeLimitKind = SizeLimitKind.RETURN) -> str:
        """
        Get the content of a file as a string.
        """

        full_path = self._build_path(path)
        self._check_file_size_is_not_too_large(full_path, size_limit_kind)
        self._require_path_is_in_excluded_folder(full_path)

        with open(full_path, "r", encoding="utf-8", errors='replace') as f:
            return f.read()

    def get_image_file_format(self, path: str) -> str:
        """
        Get the image file format from the file extension.
        """
        ext = os.path.splitext(path)[1].lower()
        if ext == ".png":
            return "png"
        elif ext in [".jpg", ".jpeg"]:
            return "jpg"
        raise ValueError(f"Unsupported image format: {ext}")

    def _check_file_size_is_not_too_large(self, full_path: str, size_limit_kind: SizeLimitKind = SizeLimitKind.RETURN):
        """
        Check if the file size is not too large.
        """
        stat = os.stat(full_path)

        if size_limit_kind == SizeLimitKind.READ:
            if self.config.max_read_file_size is not None and stat.st_size > self.config.max_read_file_size:
                raise ValueError(f"File {full_path} is too large to download.")

        elif size_limit_kind == SizeLimitKind.RETURN:
            if self.config.max_return_file_size is not None and stat.st_size > self.config.max_return_file_size:
                raise ValueError(f"File {full_path} is too large to return.")

    def _require_path_is_in_excluded_folder(self, path: str):
        """
        Raise an error if the given path is in any of the excluded folders.
        """
        if self._check_path_is_in_excluded_folder(path):
            raise ValueError(f"Path {path} is not found.")
    
    def _check_path_is_in_excluded_folder(self, path: str) -> bool:
        """
        Check if the given path is in any of the excluded folders.
        """
        return any(path.startswith(excluded) for excluded in self.config.exclude_folders)
    
    def _build_path(self, relative_path: str) -> str:
        """
        Build the absolute path for a given relative path.
        """

        if relative_path == "" or relative_path == "/" or not relative_path or relative_path == ".":
            return self.config.file_system_path

        # some tricks to protect against path traversal
        path = os.path.join(self.config.file_system_path, relative_path)
        abs_path = os.path.abspath(path)
        base_dir = os.path.abspath(self.config.file_system_path)
        # Use os.path.commonpath to check if abs_path is within base_dir
        if os.path.commonpath([abs_path, base_dir]) != base_dir:
            raise ValueError("Access to the path is not allowed.")
        return abs_path
