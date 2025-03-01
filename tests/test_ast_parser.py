import ast
from meta_loop.ast_parser import (
    get_function_signature,
    get_class_signature,
    extract_definitions_with_signatures,
)


def test_get_function_signature():
    # Test function with no parameters
    node = ast.parse("def foo(): pass").body[0]
    assert get_function_signature(node) == "foo()"

    # Test function with parameters and annotations
    node = ast.parse("def foo(a: int, b: str) -> None: pass").body[0]
    assert get_function_signature(node) == "foo(a: int, b: str) -> None"

    # Test function with default values
    node = ast.parse("def foo(a=1, b='default'): pass").body[0]
    assert get_function_signature(node) == "foo(a = 1, b = 'default')"

    # Test function with *args and **kwargs
    node = ast.parse("def foo(*args, **kwargs): pass").body[0]
    assert get_function_signature(node) == "foo(*args, **kwargs)"


def test_get_class_signature():
    # Test class with no inheritance
    node = ast.parse("class Foo: pass").body[0]
    assert get_class_signature(node) == "Foo"

    # Test class with single inheritance
    node = ast.parse("class Foo(Bar): pass").body[0]
    assert get_class_signature(node) == "Foo(Bar)"

    # Test class with multiple inheritance
    node = ast.parse("class Foo(Bar, Baz): pass").body[0]
    assert get_class_signature(node) == "Foo(Bar, Baz)"


def test_extract_definitions_with_signatures(tmp_path):
    # Create a temporary Python file
    code = """
def foo(a, b):
    pass

class Bar:
    pass
"""
    file_path = tmp_path / "temp.py"
    file_path.write_text(code)

    # Extract definitions
    functions, classes = extract_definitions_with_signatures(str(tmp_path))

    # Check extracted function signatures
    assert functions == [("foo(a, b)", str(file_path))]

    # Check extracted class signatures
    assert classes == [("Bar", str(file_path))]
