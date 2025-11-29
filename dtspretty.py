#!/usr/bin/env python3

import sys, argparse
import yaml
import json
import re
import os.path as path
from dts_parser import parse_dts_content
from parse_dts_symbols import parse_dts_symbols
from dereference_phandles import dereference_phandles
from generate_restored_dts import generate_restored_dts

def load_yaml_rules(rules_path):
    """Load dereferencing rules from YAML content."""
    rules = recursive_load_yaml(rules_path)

    # Normalize rules to ensure all entries are dictionaries
    for key, value in rules.items():
        if key[0] == '$':
            continue
        elif isinstance(value, list):
            # Treat a list directly as a struct
            rules[key] = {"patterns": [f'^{key}$'], "struct": value}
        elif isinstance(value, dict):
            # Ensure the dictionary has 'patterns' or 'struct'
            rules[key].setdefault("patterns", [f'^{key}$'])
        else:
            raise ValueError(f"Unexpected rule format for key '{key}': {value}")
    
    return rules

def recursive_load_yaml(rules_path):
    # Load YAML rules
    with open(rules_path, "r") as f:
         rules = yaml.safe_load(f.read())

    if "$extends" in rules:
        for e in rules["$extends"]:
            base_path = path.join(path.dirname(rules_path), e)
            base_rules = recursive_load_yaml(base_path)
            rules = base_rules | rules

    return rules

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore references in decompiled DTS")
    parser.add_argument("-r", "--rules", help="Rules file (YAML)")
    parser.add_argument(metavar="/path/to/decompiled.dts", dest="src", help="input file")
    args = parser.parse_args()

    if args.src.endswith(".dtb"):
        # Convert DTB to DTS before running own parser
        import fdt
        with open(args.src, "rb") as f:
            dt = fdt.parse_dtb(f.read())
            dts_content = dt.to_dts(2)
    else:
        # Load DTS content (decompiled)
        with open(args.src, "r") as f:
            dts_content = f.read()

    # Parse DTS into a structured format (JSON or dictionary)
    dts = parse_dts_content(dts_content)

    # Load symbols and rules
    phandle_to_path, path_to_symbol = parse_dts_symbols(dts)
    rules = load_yaml_rules(args.rules)

    # Restore references
    restored_dts = dereference_phandles(dts, phandle_to_path, path_to_symbol, rules)

    # Generate output DTS
    output_dts = generate_restored_dts(restored_dts, path_to_symbol)
    print(output_dts)
