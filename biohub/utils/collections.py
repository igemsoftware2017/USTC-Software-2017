def unique(seq):
    """
    Remove duplicated items in a sequence whilst preserving the order.
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
