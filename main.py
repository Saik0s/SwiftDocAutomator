import argparse
import logging
import os
import tempfile
from typing import Tuple

from tree_sitter import Language, Node, Parser, Tree, TreeCursor

from summarize import generate_class_body_summary, generate_combined_summary, generate_function_summary

logging.basicConfig(level=logging.INFO)

SWIFT_LANGUAGE: Language = Language("build/languages.so", "swift")


def edit_function_declarations(tree: Tree, source: str) -> str:
    # Initialize a tree cursor and data structures for class and function summaries
    cursor: TreeCursor = tree.walk()
    class_summaries = {}
    function_summaries = []

    # Process class declarations and their children
    def process_class_declarations(cursor: TreeCursor) -> None:
        nonlocal class_summaries
        node: Node = cursor.node
        if node.type == "class_declaration":
            first_line = node.text.decode("utf-8").split("\n")[0]
            logging.info(f"Processing class declaration: {first_line}")
            class_summaries[node.id] = []
            class_body = next((child for child in node.children if child.type == "class_body"), None)
            if class_body:
                process_function_declarations(class_body)
            if not class_summaries[node.id]:
                class_summaries[node.id] = node
        if cursor.goto_first_child():
            process_class_declarations(cursor)
            while cursor.goto_next_sibling():
                process_class_declarations(cursor)
            cursor.goto_parent()

    # Process function and property declarations within a class
    def process_function_declarations(class_node: Node) -> None:
        nonlocal function_summaries
        for node in class_node.children:
            if node.type in ["function_declaration", "property_declaration"]:
                first_line = node.text.decode("utf-8").split("\n")[0]
                logging.info(f"Processing function/property declaration: {first_line}")
                summary: str = generate_function_summary(node)
                parent = node.parent
                grandparent = parent.parent if parent else None
                if grandparent and grandparent.type == "class_declaration":
                    class_summaries[grandparent.id].append((node, summary))
                function_summaries.append((node, summary))

    # Process class and function declarations in the tree
    process_class_declarations(cursor)
    process_function_declarations(tree.root_node)

    # Combine summaries
    summaries = function_summaries

    for _, children in class_summaries.items():
        if isinstance(children, list):
            concatenated_summary = generate_combined_summary([summary for _, summary in children])
            summaries.append((children[0][0].parent.parent, concatenated_summary))
        elif isinstance(children, Node):
            concatenated_summary = generate_class_body_summary(children.text.decode("utf8"))
            summaries.append((children, concatenated_summary))
        else:
            logging.error(f"Unexpected type {type(children)}")

    # Sort summaries by start byte
    summaries.sort(key=lambda x: x[0].start_byte)

    # Insert summaries into the source code
    for node, summary in reversed(summaries):
        indent: str = " " * node.start_point[1]
        summary = "\n".join([f"{indent}{line}" for line in summary.split("\n")])
        summary = f"{summary[node.start_point[1]:]}\n{indent}"
        source = source[: node.start_byte] + summary.encode("utf8") + source[node.start_byte :]

    return source


def insert_summary(file_path: str, new_code: str) -> None:
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(new_code)
    os.replace(temp_file.name, file_path)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add documentation to Swift file.")
    parser.add_argument("file_path", type=str, help="Path to the Swift file.")
    return parser.parse_args()


def read_swift_file(file_path: str) -> Tuple[str, bytes]:
    with open(file_path, "r") as f:
        original: str = f.read()
    as_bytes = bytes(original, "utf8")
    return original, as_bytes


def parse_swift_source(source: bytes) -> Tree:
    swift_parser: Parser = Parser()
    swift_parser.set_language(SWIFT_LANGUAGE)
    return swift_parser.parse(source)


if __name__ == "__main__":
    args = parse_arguments()
    file_path: str = args.file_path
    original, as_bytes = read_swift_file(file_path)
    tree = parse_swift_source(as_bytes)

    new_code = edit_function_declarations(tree, as_bytes).decode("utf8")
    insert_summary(file_path, new_code)
