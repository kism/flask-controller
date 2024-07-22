"""Unit test the controller module."""

import random
import string

from flaskcontroller.controller import colour_player_id


def test_colour_player_id():
    """TEST: The colour ID generator runs without issue."""
    random_strings = []
    for _ in range(1000):
        length = random.randint(0, 10)
        random_string = "".join(random.choices(string.ascii_letters + string.digits, k=length))
        random_strings.append(random_string)

    for my_string in random_string:
        colour_player_id(my_string)
