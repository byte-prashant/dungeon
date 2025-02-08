import astor, ast
class MethodReplacer(ast.NodeTransformer):

    def __init__(self, class_name, method_name, new_method_body):
        self.class_name = class_name
        self.method_name = method_name
        self.new_method_body = new_method_body

    def visit_ClassDef(self, node):
        # Check if the class is the one we want
        if node.name == self.class_name:
            for i, item in enumerate(node.body):
                if isinstance(item, ast.FunctionDef) and item.name == self.method_name:
                    # Replace the method definition
                    new_method = ast.parse(self.new_method_body).body[0]
                    node.body[i] = new_method
                    break
        return node


def replace_method_in_file(file_path, class_name, method_name, new_method_body):
    """
    Replace a method definition in a specified class within a Python file.

    Args:
        file_path (str): Path to the Python file.
        class_name (str): Name of the class containing the method.
        method_name (str): Name of the method to replace.
        new_method_body (str): The new method implementation as a string.

    Returns:
        None
    """
    try:
        # Parse the Python file
        with open(file_path, "r") as file:
            tree = ast.parse(file.read())

        # Replace the method
        replacer = MethodReplacer(class_name, method_name, new_method_body)
        modified_tree = replacer.visit(tree)

        # Write the modified code back to the file
        with open(file_path, "w") as file:
            file.write(astor.to_source(modified_tree))

        print(f"Method '{method_name}' in class '{class_name}' replaced successfully.")
    except Exception as e:
        print(f"Error: {e}")