def format_idr(value):
    """Format float to Indonesian Rupiah style (Gold). e.g. 1.234.567"""
    try:
        return f"{float(value):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return str(value)

def format_decimal_id(value):
    """Format float to Indonesian decimal style (IHSG). e.g. 7.200,50"""
    try:
        # Step 1: Use US format e.g. 7,200.50
        us_format = f"{float(value):,.2f}"
        # Step 2: Swap dot and comma
        return us_format.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    except (ValueError, TypeError):
        return str(value)
