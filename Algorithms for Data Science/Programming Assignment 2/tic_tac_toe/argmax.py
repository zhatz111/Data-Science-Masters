# Returns the index of the maximum value in a list of values
def argmax(scores: list) -> int:
    max_index = max(
        range(len(scores)),
        key=lambda i: scores[i])
    return max_index