import re

def parse_dts_symbols(dts_content):
    """Extract __symbols__ mapping and phandles from DTS content."""
    symbols = {}
    phandles = {}
    current_path_stack = []
    current_path = "/"

    for line in dts_content.splitlines():
        line = line.strip()

        # Track the current node path
        if line.endswith("{"):
            # Start of a new node
            node_name = line.split("{")[0].strip()
            if ":" in node_name:
                node_name = node_name.split(":")[0]  # Remove labels like `xin24m:`
            current_path_stack.append(current_path)
            current_path = f"{current_path.rstrip('/')}/{node_name.lstrip('/')}".replace("//", "/")
        elif line == "};":
            # End of a node
            current_path = current_path_stack.pop()

        # Parse __symbols__ section
        if line.startswith('__symbols__ {'):
            inside_symbols = True
            continue
        elif line == "};":  # End of __symbols__
            inside_symbols = False
            continue
        elif line.startswith("__symbols__") or "inside_symbols" in locals() and inside_symbols:
            match = re.match(r"(\w+)\s*=\s*\"([^\"]+)\";", line)
            if match:
                symbol_name = match.group(1)
                symbol_path = match.group(2)
                symbols[symbol_name] = symbol_path

        # Parse phandle values
        phandle_match = re.search(r"phandle\s*=\s*<(\w+)>;", line)
        if phandle_match:
            phandle_value = int(phandle_match.group(1), 0)  # Convert phandle to integer
            phandles[phandle_value] = current_path.rstrip("/")

    # Merge phandles into symbols for unified reference
    symbols.update(phandles)
    return symbols

if __name__ == "__main__":
    # Example DTS content (decompiled)
    dts_content = """
    /dts-v1/;

    / {
        xin24m {
            #clock-cells = <0x00>;
            phandle = <0x01>;
        };

        clock-controller@ff2b0000 {
            compatible = "rockchip,px30-cru";
            phandle = <0x03>;
        };

        clock-controller@ff2bc000 {
            compatible = "rockchip,px30-pmucru";
            phandle = <0x02>;
        };

        i2c0 {
            i2c0-xfer {
                phandle = <0x06>;
            };

            sfc-clk {
                phandle = <0x05>;
            };
        };

        pcfg-pull-none-smt {
            phandle = <0x04>;
        };

        __symbols__ {
            xin24m = "/xin24m";
            cru = "/clock-controller@ff2b0000";
            pmucru = "/clock-controller@ff2bc000";
            sfc_cs0 = "/i2c0/i2c0-xfer";
            sfc_clk = "/i2c0/sfc-clk";
            pcfg_pull_none_smt = "/pcfg-pull-none-smt";
        };
    };
    """

    symbols = parse_dts_symbols(dts_content)
    print(symbols)
