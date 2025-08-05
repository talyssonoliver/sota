"""
Centralized File Operations Utilities
Common functions for file and directory operations
"""

import json
import yaml
from pathlib import Path
from typing import Any, List, Union, Iterator
import shutil


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if necessary"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_file(
    file_path: Union[str, Path],
    encoding: str = 'utf-8',
    errors: str = 'strict'
) -> str:
    """Read text file contents"""
    with open(file_path, 'r', encoding=encoding, errors=errors) as f:
        return f.read()


def write_file(
    file_path: Union[str, Path],
    content: str,
    encoding: str = 'utf-8',
    create_dirs: bool = True
) -> None:
    """Write content to text file"""
    file_path = Path(file_path)
    
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)


def load_json(
    file_path: Union[str, Path],
    default: Any = None,
    encoding: str = 'utf-8'
) -> Any:
    """Load JSON file"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        if default is not None:
            return default
        raise


def save_json(
    data: Any,
    file_path: Union[str, Path],
    pretty: bool = True,
    encoding: str = 'utf-8',
    create_dirs: bool = True
) -> None:
    """Save data to JSON file"""
    file_path = Path(file_path)
    
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding=encoding) as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, f, ensure_ascii=False)


def load_yaml(
    file_path: Union[str, Path],
    default: Any = None,
    encoding: str = 'utf-8'
) -> Any:
    """Load YAML file"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return yaml.safe_load(f) or default
    except FileNotFoundError:
        if default is not None:
            return default
        raise


def save_yaml(
    data: Any,
    file_path: Union[str, Path],
    encoding: str = 'utf-8',
    create_dirs: bool = True
) -> None:
    """Save data to YAML file"""
    file_path = Path(file_path)
    
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding=encoding) as f:
        yaml.dump(data, f, default_flow_style=False)


def copy_file(
    src: Union[str, Path],
    dst: Union[str, Path],
    create_dirs: bool = True
) -> Path:
    """Copy file to destination"""
    src = Path(src)
    dst = Path(dst)
    
    if create_dirs:
        dst.parent.mkdir(parents=True, exist_ok=True)
    
    return Path(shutil.copy2(src, dst))


def move_file(
    src: Union[str, Path],
    dst: Union[str, Path],
    create_dirs: bool = True
) -> Path:
    """Move file to destination"""
    src = Path(src)
    dst = Path(dst)
    
    if create_dirs:
        dst.parent.mkdir(parents=True, exist_ok=True)
    
    return Path(shutil.move(str(src), str(dst)))


def delete_file(
    file_path: Union[str, Path],
    missing_ok: bool = True
) -> bool:
    """Delete file"""
    try:
        Path(file_path).unlink()
        return True
    except FileNotFoundError:
        if missing_ok:
            return False
        raise


def list_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False
) -> List[Path]:
    """List files in directory"""
    directory = Path(directory)
    
    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))


def get_file_size(file_path: Union[str, Path]) -> int:
    """Get file size in bytes"""
    return Path(file_path).stat().st_size


def get_file_hash(
    file_path: Union[str, Path],
    algorithm: str = 'sha256'
) -> str:
    """Calculate file hash"""
    import hashlib
    
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def read_lines(
    file_path: Union[str, Path],
    encoding: str = 'utf-8',
    skip_empty: bool = False
) -> List[str]:
    """Read file as list of lines"""
    lines = read_file(file_path, encoding).splitlines()
    
    if skip_empty:
        lines = [line for line in lines if line.strip()]
    
    return lines


def write_lines(
    lines: List[str],
    file_path: Union[str, Path],
    encoding: str = 'utf-8',
    create_dirs: bool = True
) -> None:
    """Write list of lines to file"""
    content = '\n'.join(lines)
    if lines and not content.endswith('\n'):
        content += '\n'
    
    write_file(file_path, content, encoding, create_dirs)


def iterate_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = True
) -> Iterator[Path]:
    """Iterate over files in directory"""
    directory = Path(directory)
    
    if recursive:
        yield from directory.rglob(pattern)
    else:
        yield from directory.glob(pattern)
