"""Update the README installer pin without downgrading an existing release."""

from pathlib import Path
import re
import sys


VERSION = r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)'


def pin_release(path: Path, tag: str) -> None:
    version = re.fullmatch(VERSION, tag)
    if version is None:
        raise ValueError('release tag must be vMAJOR.MINOR.PATCH')
    text = path.read_text(encoding='utf-8')
    pins = list(re.finditer(r'^  tag="(' + VERSION + r')"$', text, re.MULTILINE))
    if len(pins) != 1:
        raise ValueError('README must contain exactly one installer tag pin')
    current = re.fullmatch(VERSION, pins[0][1])
    if tuple(map(int, version.groups())) > tuple(map(int, current.groups())):
        pin = pins[0]
        path.write_text(text[:pin.start(1)] + tag + text[pin.end(1):], encoding='utf-8')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: pin-release.py vMAJOR.MINOR.PATCH')
    try:
        pin_release(Path('README.md'), sys.argv[1])
    except ValueError as error:
        raise SystemExit(str(error))
