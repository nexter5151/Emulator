def parse_input(line):
    parts = line.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]
