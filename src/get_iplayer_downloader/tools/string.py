def str2bool(string):
    return string and string.lower() in ("yes", "true", "1")

def str2float(string):
    try:
        return float(string)
    except ValueError:
        return 0.0

#def decode(string):
#    # Simple decoding
#    #return string.decode("LATIN-1", "replace")
#    return string.decode("UTF-8", "replace")
