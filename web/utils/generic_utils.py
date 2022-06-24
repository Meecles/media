import random
import string


def rand_str(length):
    lowers = string.ascii_lowercase
    uppers = string.ascii_uppercase
    letters = [letter for letter in "{}{}".format(lowers, uppers)]
    random.shuffle(letters)
    return ''.join(random.choice(letters) for i in range(length))
