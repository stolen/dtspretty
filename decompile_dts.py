import sys, argparse
import yaml
import json
import re
from dts_parser import parse_dts_content
from parse_dts_symbols import parse_dts_symbols

def load_yaml_rules(yaml_content):
    """Load dereferencing rules from YAML content."""
    rules = yaml.safe_load(yaml_content)

    # Normalize rules to ensure all entries are dictionaries
    for key, value in rules.items():
        if isinstance(value, list):
            # Treat a list directly as a struct
            rules[key] = {"struct": value}
        elif isinstance(value, dict):
            # Ensure the dictionary has 'patterns' or 'struct'
            rules[key].setdefault("patterns", [])
        else:
            raise ValueError(f"Unexpected rule format for key '{key}': {value}")
    
    return rules


def dereference_phandles(dts, symbols, rules):
    """Restore references in the DTS structure."""
    def resolve_property(prop, value):
        """Resolve property references based on rules."""
        for rule_name, rule in rules.items():
            patterns = rule.get('patterns', [])
            struct = rule.get('struct', 'dynamic')
            for pattern in patterns:
                if re.match(pattern, prop):
                    return resolve_struct(value, struct)
        # Default to dynamic resolution if no patterns match
        return resolve_struct(value, 'dynamic')
    
    def resolve_struct(value, struct):
        """Resolve a property value based on its struct."""
        if not isinstance(value, list):
            value = [value]  # Ensure value is a list for processing
        resolved = []
        if struct == 'dynamic':
            i = 0
            while i < len(value):
                # Check if value[i] is a reference (phandle) and resolve it
                if isinstance(value[i], int):  # If the value is an integer (phandle)
                    ref = symbols.get(value[i], hex(value[i]))  # Try to resolve using symbols
                    resolved.append(f"&{ref.lstrip('/')}" if ref.startswith("/") else ref)
                else:
                    resolved.append(value[i])
                i += 1
        else:
            # Handle fixed structs (e.g., rockchip,pins)
            for idx, item in enumerate(struct):
                if idx >= len(value):
                    break
                if item == "ref":
                    # Resolve phandle to a symbolic reference
                    ref = symbols.get(value[idx], hex(value[idx])) if isinstance(value[idx], int) else value[idx]
                    resolved.append(f"&{ref.lstrip('/')}" if ref.startswith("/") else ref)
                else:
                    resolved.append(value[idx])
        return resolved
    
    def process_node(node):
        """Recursively process a node."""
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, dict):
                    process_node(value)
                elif isinstance(value, list):
                    node[key] = [resolve_property(key, v) if isinstance(v, (int, list)) else v for v in value]
                else:
                    node[key] = resolve_property(key, value) if isinstance(value, (int, list)) else value

    process_node(dts)
    return dts

def generate_restored_dts(dts):
    """Generate DTS file content from the restored structure."""
    # Implement DTS generation logic
    # For simplicity, we return a JSON string in this example
    return json.dumps(dts, indent=2)

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore references in decompiled DTS")
    parser.add_argument("-r", "--rules", help="Rules file (YAML)")
    parser.add_argument(metavar="/path/to/decompiled.dts", dest="src", help="input file")
    args = parser.parse_args()

    # Load DTS content (decompiled)
    with open(args.src, "r") as f:
        dts_content = f.read()

    # Load YAML rules
    with open(args.rules, "r") as f:
        yaml_content = f.read()

    # Load symbols and rules
    symbols = parse_dts_symbols(dts_content)
    rules = load_yaml_rules(yaml_content)

    # Parse DTS into a structured format (JSON or dictionary)
    dts = parse_dts_content(dts_content)

    # Restore references
    restored_dts = dereference_phandles(dts, symbols, rules)

    # Generate output DTS
    output_dts = generate_restored_dts(restored_dts)
    print(output_dts)
    #print(json.dumps(symbols, indent=2))
