def run_command(command, args):
    if command == "ls":
        if args:
            return "ls: " + " ".join(args), False
        return "ls", False

    if command == "cd":
        if args:
            return "cd: " + " ".join(args), False
        return "cd", False

    if command == "exit":
        return "", True

    return command + ": command not found", False
