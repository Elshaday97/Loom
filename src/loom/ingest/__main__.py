import ast
import json
import textwrap
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from sentence_transformers import SentenceTransformer

from loom.utils import OUTPUT_PATH


@dataclass
class Chunk:
    id: str
    kind: str
    name: str | None
    path: str
    start_line: int
    end_line: int
    text: str


class Chunker:
    def __init__(self, files_to_chunk: list[str], model: SentenceTransformer):
        self.files_to_chunk = files_to_chunk
        self.tokenizer = model.tokenizer
        self.max_token_size = model.max_seq_length

        self.chunks: list = []
        self.current_file:str = None
        self.assignment_buffer = []
        self.assignment_group_start=None
        self.assignment_group_end=None

    def chunk_files(self):
        try:
            if not isinstance(self.files_to_chunk, list) or self.files_to_chunk is None:
                raise TypeError("File paths should be a list.")

            for file_path in self.files_to_chunk:
                print(f"Reading file and processing: {file_path}")
                self.current_file = file_path
                source = Path(file_path).read_text(encoding="utf-8")
                lines = source.splitlines()
                tree = ast.parse(source=source)
                nodes = ast.iter_child_nodes(tree)

                for node in nodes:
                    if node is not None:
                        self.__fork_node(node=node, lines=lines)

                # Check remaining assignment lines
                self.__chunk_assignment_buffer()
                
                print("Finished chunking files")

            if self.chunks is not None:
                print("Exporting chunks...")
                self.__export_chunks()

            self.__clear_class()

        except (OSError, TypeError, SyntaxError, UnicodeDecodeError, ValueError) as e:
            print(f"Error Preparing Nodes: {e}")
    
    def __fork_node(self, node: ast.AST, lines: list[str]):
        try:
            if node is not None:
                if(isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef))):
                    self.__chunk_methods(node, lines)
                elif(isinstance(node, ast.Assign)):
                    self.__process_buffer(node, lines, buffer_type="assignment")
                elif(isinstance(node, ast.ClassDef)):
                    self.__chunk_classes(node, lines)
        except (OSError, TypeError, SyntaxError, UnicodeDecodeError, ValueError) as e:
            print(f"Error Forking Nodes: {e}")
   
    def __chunk_methods(self, node: ast.AST, lines: list[str]): 
        try:
            start = node.lineno
            end = node.end_lineno

            text = "\n".join(lines[start-1:end])
            can_chunk_text = self.__is_valid_token_size(text)

            if(can_chunk_text):
                self.__apply_chunk(text, type(node).__name__, node.name, start, end, self.current_file)
                return
            else:
                self.__process_buffer(node, lines, "method")
            return
        except (OSError, TypeError, SyntaxError, UnicodeDecodeError, ValueError) as e:
            print(f"Error Chunking Methods: {e}")
  
    def __chunk_assignment_buffer(self):
        try:
            if len(self.assignment_buffer):
                buffer_text = "\n".join(self.assignment_buffer)
                self.__apply_chunk(buffer_text, "Assignment", "Assignment",self.assignment_group_start, self.assignment_group_end, self.current_file)
                self.assignment_buffer.clear()
        except (OSError, TypeError, SyntaxError, UnicodeDecodeError, ValueError) as e:
            print(f"Error Chunking Assignment Buffer: {e}")

    def __process_buffer(self, node: ast.AST, lines: list[str],  buffer_type: Literal["method" , "assignment"] = "method", custom_start:None=None, custom_end:None=None):
        try:
            start =  custom_start if custom_start else node.lineno
            end = custom_end if custom_end else node.end_lineno
            has_custom_lines = custom_start and custom_end
            temp_start = start
            temp_end = end         
            buffer = self.assignment_buffer.copy() if buffer_type == "assignment" else []

            
            lines_in_context = lines if has_custom_lines else lines[start-1:end]

            for index, line in enumerate(lines_in_context):
                line_token_size = self.__get_token_size(line)

                if len(buffer):
                    buffer_text = "\n".join(buffer)
                    buffer_token_size = self.__get_token_size(buffer_text)

                    if(buffer_token_size + line_token_size < self.max_token_size):
                        if(buffer_type == "assignment"):
                            self.assignment_buffer.append(line)
                            self.assignment_group_end = start + index
                        buffer.append(line)
                        temp_end = start + index
                    else:
                        if(buffer_type == "assignment"):
                            self.__chunk_assignment_buffer()
                        else:
                            self.__apply_chunk(buffer_text, type(node).__name__, node.name, temp_start, temp_end, self.current_file)

                        buffer.clear()

                        if line_token_size < self.max_token_size:
                            if(buffer_type == "assignment"):
                                self.assignment_buffer.append(line)
                                self.assignment_group_end = self.assignment_group_start = start + index
                            
                            buffer.append(line)
                            temp_start = temp_end = start + index
                        else:
                            wrapped_lines = textwrap.wrap(line, width=30)
                            self.__process_buffer(node, wrapped_lines, buffer_type, start+index, start+index)
                else:
                    if(self.__is_valid_token_size(line)):
                        if(buffer_type=="assignment"):
                            self.assignment_buffer.append(line)
                        self.assignment_group_end = self.assignment_group_start = start + index
                        
                        buffer.append(line)
                        temp_end = start + index
                    else:
                        wrapped_lines = textwrap.wrap(line, width=30)
                        self.__process_buffer(node, wrapped_lines, buffer_type, start+index, start+index)


            if(buffer_type == "method" and len(buffer)):
                buffer_text = "\n".join(buffer)
                self.__apply_chunk(buffer_text, type(node).__name__, node.name, temp_start, temp_end, self.current_file)
                buffer.clear()


            return

        except (OSError, TypeError, SyntaxError, UnicodeDecodeError, ValueError) as e:
            print(f"Error Accumulating Buffer: {e}")

    def __chunk_classes(self, node: ast.AST, lines: list[str]): 
        try:
            for body in node.body:
                self.__fork_node(body, lines=lines)
        except (OSError, TypeError, SyntaxError, UnicodeDecodeError, ValueError) as e:
            print(f"Error Chunking Classes: {e}")

    def __is_valid_token_size(self, chunk:str):
        try:
            token_size = len(self.tokenizer.encode(chunk, add_special_tokens=False))
            return token_size < self.max_token_size
        except ValueError as e:
            print(f"Error Checking Token Size: {e}")

    def __get_token_size(self, chunk: str):
        try:
            return len(self.tokenizer.encode(chunk, add_special_tokens=False))
        except ValueError as e:
            print(f"Error Checking Token Size: {e}")
            
    def __apply_chunk(self, text:str, kind:str, name:str, start: int, end: int, file_path:Path):
        try:
            chunk = Chunk(f"{file_path}:{start}", kind, name, str(file_path), start, end, text)
            self.chunks.append(chunk)
            return
        except ValueError as e:
            print(f"Error Applying Chunks: {e}")
    
    def __export_chunks(self):
        try:
            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                f.write("\n".join(json.dumps(asdict(chunk)) for chunk in self.chunks) + "\n")
            return f"Chunk exported in {OUTPUT_PATH}"

        except (OSError, TypeError, SyntaxError, UnicodeDecodeError, ValueError) as e:
            print(f"Error Exporting Chunks: {e}")

    def __clear_class(self):
        self.current_file = None
        self.chunks = []
        self.assignment_buffer = []
        self.assignment_group_start=None
        self.assignment_group_end=None