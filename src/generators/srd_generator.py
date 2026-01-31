def generate_srd(endpoints):
    lines = ["BUSINESS SRD", "==============", ""]

    for ep in endpoints:
        lines.append(f"Endpoint:")
        lines.append(f"  Method : {ep.http_method}")
        lines.append(f"  Handler: {ep.handler}")
        lines.append(f"  Source : {ep.file}")
        lines.append("")

    return "\n".join(lines)
