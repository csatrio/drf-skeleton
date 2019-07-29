def check_exclusion(word, excludes):
    for e in excludes:
        if e in word:
            return False
    return True
