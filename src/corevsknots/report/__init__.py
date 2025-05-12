# Make generate_report available from the report package
from .markdown_generator import generate_report

__all__ = ["generate_report"]
