# __init__.py

__author__ = "Abyss"
__version__ = "0.0.1"
__license__ = "GPL"
__description__ = "A simple file system simulator for educational purposes."

from .models import File, Directory, FileSystem

__all__ = ["File", "Directory", "FileSystem"]