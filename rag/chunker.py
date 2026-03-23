"""Codebase chunking with tree-sitter."""

import tree_sitter_python
from tree_sitter import Language, Parser, Node
from typing import TypedDict

# Minimal AST chunking for Python MVP
PY_LANGUAGE = Language(tree_sitter_python.language(), "python")

class CodeChunk(TypedDict):
    content: str
    chunk_type: str
    start_line: int
    end_line: int

def chunk_file(file_path: str, content: str, language: str = "python") -> list[CodeChunk]:
    """Parse a file and chunk it by functions and classes using tree-sitter."""
    if language != "python":
        # Fallback for non-python: chunk by lines (MVP simplification)
        lines = content.splitlines()
        return [{"content": content, "chunk_type": "file", "start_line": 1, "end_line": len(lines)}]
        
    parser = Parser(PY_LANGUAGE)
    tree = parser.parse(bytes(content, "utf8"))
    
    chunks: list[CodeChunk] = []
    
    def traverse(node: Node) -> None:
        if node.type in ["function_definition", "class_definition"]:
            chunk_content = content[node.start_byte:node.end_byte]
            chunks.append({
                "content": chunk_content,
                "chunk_type": "function" if node.type == "function_definition" else "class",
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1
            })
            # Skip traversing inside functions to avoid nested chunks overlap
            if node.type == "function_definition":
                return
                
        for child in node.children:
            traverse(child)
            
    traverse(tree.root_node)
    
    # If no functions/classes found, return the whole file as a chunk
    if not chunks:
        lines = content.splitlines()
        return [{"content": content, "chunk_type": "module", "start_line": 1, "end_line": len(lines)}]
        
    return chunks
