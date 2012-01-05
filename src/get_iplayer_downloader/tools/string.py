
def str2bool(string):
    return string and string.lower() in ("yes", "true", "1")

def decode(string):
    # Simple decoding
    return string.decode('utf8', "replace")
