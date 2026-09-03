"""End to end: a real browser, driving the real page, against a real server, talking to a fake GBA client.

Skipped unless the e2e extra is installed, run with `--extra e2e` after `playwright install chromium`.
"""

import pytest

from webcontroller.services.controller import Button

pytest.importorskip("playwright")  # The e2e extra isn't installed for the plain unit test run.

from playwright.sync_api import Page, expect

# The keys home.ts maps to buttons, see its keymap.
KEY_A = "x"
KEY_B = "z"
KEY_UP = "ArrowUp"

HELD_COLOUR = "rgb(0, 63, 135)"


def test_status_shows_the_emulator_connection(page: Page, live_url: str) -> None:
    """TEST: The page polls /status and reports the socket to the fake GBA client, and itself as a player."""
    page.goto(live_url)

    expect(page.locator("#SOCKET_STATUS")).to_have_text("Connected")
    expect(page.locator("#PLAYER_COUNT")).to_have_text("1")


def test_keypress_reaches_the_fake_gba(page: Page, live_url: str, fake_gba) -> None:
    """TEST: A keypress in the browser arrives at the emulator as the button's bitmask, and clears on keyup."""
    page.goto(live_url)

    page.keyboard.down(KEY_A)
    expect(page.locator("#GBA_A")).to_have_css("background-color", HELD_COLOUR)
    assert fake_gba.wait_for_states([Button.GBA_A.bit]), f"Got {fake_gba.states}"

    page.keyboard.up(KEY_A)
    assert fake_gba.wait_for_states([Button.GBA_A.bit, 0]), f"Got {fake_gba.states}"

    # The latency stat is only rendered once an input has round tripped.
    expect(page.locator("#HTTP_LATENCY")).to_contain_text("frame")


def test_held_buttons_combine(page: Page, live_url: str, fake_gba) -> None:
    """TEST: Buttons held at the same time arrive as one combined bitmask, mGBA needs the whole state each time."""
    page.goto(live_url)

    # home.ts fires each POST without awaiting the last, so give them a beat to arrive in order, as a human would.
    page.keyboard.down(KEY_B)
    page.wait_for_timeout(50)
    page.keyboard.down(KEY_UP)
    page.wait_for_timeout(50)
    page.keyboard.up(KEY_B)

    expected = [Button.GBA_B.bit, Button.GBA_B.bit | Button.GBA_UP.bit, Button.GBA_UP.bit]
    assert fake_gba.wait_for_states(expected), f"Got {fake_gba.states}"
