BINARY_MISSING_VAL = -1

ALLOWED_CHARS = set([chr(x) for x in range(128)
                     if x not in set(list(range(9)) + [11, 12] + list(range(14, 32)) + [127])])
