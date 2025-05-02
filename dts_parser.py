import re

def parse_dts_content(dts_content):
    """Parse DTS content into a structured dictionary."""
    dts = {}
    stack = [dts]
    node_stack = ["/"]
    current_node = dts

    for line in dts_content.splitlines():
        line = line.strip()
        if not line or line.startswith("/dts-v1") or line.startswith("/"):
            # Skip unnecessary lines
            continue

        if line.endswith("{"):
            # Start of a new node
            node_name = line[:-1].strip()
            if ":" in node_name:
                node_name = node_name.split(":")[0]  # Remove labels like `xin24m:`
            new_node = {}
            current_node[node_name] = new_node
            stack.append(current_node)
            current_node = new_node
            node_stack.append(node_name)
        elif line.endswith("};"):
            # End of a node
            current_node = stack.pop()
            node_stack.pop()
        elif "=" in line:
            # Property assignment
            key, value = map(str.strip, line.split("=", 1))
            value = value.rstrip(";")
            if value.startswith("<") and value.endswith(">"):
                # Parse numeric array
                value = [int(v, 0) if v.startswith("0x") else int(v) for v in value[1:-1].split()]
            elif value.startswith('"') and value.endswith('"'):
                # Parse string
                value = value.strip('"')
            elif re.match(r"^[0-9a-fx]+$", value, re.IGNORECASE):
                # Parse single numeric value
                value = int(value, 0)
            elif value.startswith("[") and value.endswith("]"):
                # Parse array of strings
                value = [v.strip('"') for v in value[1:-1].split(",")]
            current_node[key] = value

    return dts

# Example usage
if __name__ == "__main__":
    # Example DTS content (decompiled)
    dts_content = """
    /dts-v1/;

    / {
        #address-cells = <0x02>;
        #size-cells = <0x02>;

        xin24m {
            #clock-cells = <0x00>;
            phandle = <0x01>;
        };

        clock-controller@ff2b0000 {
            compatible = "rockchip,px30-cru";
            reg = <0x00 0xff2b0000 0x00 0x1000>;
            clocks = <0x01 0x02 0x01>;
            clock-names = "xin24m\0gpll";
            #clock-cells = <0x01>;
            #reset-cells = <0x01>;
            assigned-clocks = <0x03 0x04 0x03 0x140 0x03 0x49>;
            assigned-clock-rates = <0x46cf7100 0x5f5e100 0xbebc200>;
            phandle = <0x03>;
        };

        clock-controller@ff2bc000 {
            compatible = "rockchip,px30-pmucru";
            reg = <0x00 0xff2bc000 0x00 0x1000>;
            clocks = <0x01>;
            clock-names = "xin24m";
            #clock-cells = <0x01>;
            #reset-cells = <0x01>;
            phandle = <0x02>;
        };

        __symbols__ {
            xin24m = "/xin24m";
            cru = "/clock-controller@ff2b0000";
            pmucru = "/clock-controller@ff2bc000";
        };
    };
    """

    dts_dict = parse_dts_content(dts_content)
    import json
    print(json.dumps(dts_dict, indent=2))