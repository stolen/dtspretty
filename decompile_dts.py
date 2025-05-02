import sys, argparse
import yaml
import json
import re
from dts_parser import parse_dts_content

def load_yaml_rules(yaml_content):
    """Load dereferencing rules from YAML content."""
    return yaml.safe_load(yaml_content)

def parse_dts_symbols(dts_content):
    """Extract __symbols__ mapping from DTS content."""
    symbols = {}
    inside_symbols = False

    for line in dts_content.splitlines():
        line = line.strip()
        if line.startswith('__symbols__ {'):
            inside_symbols = True
        elif inside_symbols and line == '};':
            break
        elif inside_symbols:
            match = re.match(r'(\w+)\s*=\s*"/([^"]+)";', line)
            if match:
                symbols[match.group(1)] = match.group(2)
    
    return symbols

def dereference_phandles(dts, symbols, rules):
    """Restore references in the DTS structure."""
    def resolve_property(prop, value):
        """Resolve property references based on rules."""
        for rule_name, rule in rules.items():
            for pattern in rule.get('patterns', []):
                if re.match(pattern, prop):
                    struct = rule.get('struct', 'dynamic')
                    return resolve_struct(value, struct)
        # Default to dynamic resolution
        return resolve_struct(value, 'dynamic')
    
    def resolve_struct(value, struct):
        """Resolve a property value based on its struct."""
        resolved = []
        if struct == 'dynamic':
            i = 0
            while i < len(value):
                ref = symbols.get(value[i], hex(value[i]))
                resolved.append(ref)
                i += 1
        return resolved
    
    for node, properties in dts.items():
        for prop, value in properties.items():
            if isinstance(value, list):
                properties[prop] = resolve_property(prop, value)
    
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
