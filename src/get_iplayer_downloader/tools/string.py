def str2bool(string):
    return string and string.lower() in ("yes", "true", "1")

def str2float(string):
    try:
        return float(string)
    except ValueError:
        return 0.0
