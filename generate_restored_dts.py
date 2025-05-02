import sys

def generate_restored_dts(restored_dts, path_to_symbol):
    """
    Generate a DTS string from the restored DTS dictionary and the path-to-symbol mapping.

    :param restored_dts: The restored DTS structure as a dictionary.
    :param path_to_symbol: A dictionary mapping paths to symbolic names.
    :return: A string representation of the DTS.
    """
    def render_node(node, path="", indent=1):
        """
        Recursively render a DTS node.
        
        :param node: The current node in the DTS structure.
        :param path: The current path in the DTS structure.
        :param indent: The current indentation level.
        :return: A string representation of the current node.
        """
        rendered = ""
        indent_str = "    " * indent  # Create indentation string
        for key, value in node.items():
            if key == 'phandle':
                continue
            current_path = f"{path}/{key}".strip("/")
            symbol = path_to_symbol.get(f"/{current_path}", None)
            
            if value == True:
                rendered += f"{indent_str}{key};\n"
            elif isinstance(value, dict):
                # Render subnodes
                node_header = f"{symbol}: {key}" if symbol else key
                rendered += f"{indent_str}{node_header} {{\n"
                rendered += render_node(value, current_path, indent + 1)
                rendered += f"{indent_str}}};\n"
            elif isinstance(value, list):
                # Render lists, including nested lists for DTS property arrays
                rendered += f"{indent_str}{key} = "
                elements = []
                for item in value:
                    if isinstance(item, str) and (item[0] == '"'):
                        # Raw strings
                        elements.append(item)
                    elif isinstance(item, list):
                        # Nested lists are rendered as grouped arrays
                        elements.append("<" + " ".join(map(str, item)) + ">")
                    else:
                        elements.append("<" + str(item) + ">")
                rendered += ", ".join(elements) + ";\n"
            else:
                print(f'rendering {key} = {value}', file=sys.stderr)
                # Render single property values
                rendered += f"{indent_str}{key} = <{value}>;\n"
        return rendered

    # Render the root node
    rendered_dts = "/dts-v1/;\n\n"
    rendered_dts += "/ {\n"
    del restored_dts['__symbols__']
    rendered_dts += render_node(restored_dts)
    rendered_dts += "};\n"

    return rendered_dts



if __name__ == "__main__":
    restored_dts = {"abc": {"def": {"foo": [["&aaa", "456"], ["&bbb"]]}}}
    path_to_symbol = {"/abc/def": "examplesym"}

    dts_text = generate_restored_dts(restored_dts, path_to_symbol)
    print(dts_text)
