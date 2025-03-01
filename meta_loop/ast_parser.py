import ast
import os


def get_function_signature(node):
    """Extract function signature from a FunctionDef node."""
    params = []
    for arg in node.args.args:
        param = arg.arg
        if arg.annotation:
            param += f": {ast.unparse(arg.annotation)}"
        params.append(param)

    # Handle default values
    defaults = [ast.unparse(d) for d in node.args.defaults]
    if defaults:
        for i, default in enumerate(defaults):
            params[-(len(defaults) - i)] += f" = {default}"

    # Handle *args and **kwargs
    if node.args.vararg:
        params.append(f"*{node.args.vararg.arg}")
    if node.args.kwarg:
        params.append(f"**{node.args.kwarg.arg}")

    # Return type annotation
    return_type = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    return f"{node.name}({', '.join(params)}){return_type}"


def get_class_signature(node):
    """Extract class signature with inheritance."""
    bases = [ast.unparse(base) for base in node.bases]
    if bases:
        return f"{node.name}({', '.join(bases)})"
    return node.name


def extract_definitions_with_signatures(repo_path):
    functions = []
    classes = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                if "tests" in root:
                    continue
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        code = f.read()
                        tree = ast.parse(code)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                sig = get_function_signature(node)
                                functions.append((sig, file_path))
                            elif isinstance(node, ast.ClassDef):
                                sig = get_class_signature(node)
                                classes.append((sig, file_path))
                    except SyntaxError:
                        print(f"Skipping {file_path} due to syntax error")
    return functions, classes


def explore_project(repo_path="meta_loop/"):

    funcs, cls = extract_definitions_with_signatures(repo_path)
    print("Functions with Signatures:")
    for func, path in funcs:
        print(f"  {func} [in {path}]")
    print("Classes with Signatures:")
    for cls_name, path in cls:
        print(f"  {cls_name} [in {path}]")


if __name__ == "__main__":
    explore_project()
