#!/usr/bin/env python3
"""Duskline One Chill — One Line, One Chill (make.fun).

Writes a single sentence of horror, under 200 characters, to
$MAKEFUN_OUTPUT_DIR/entry.txt. Python 3.13 standard library only.

The line: a photograph from the narrator's grandmother's funeral shows a
boy the narrator's own age standing behind the mourners, smiling at the
camera — and he has the narrator's face. The scare is earned, not
announced: the reader does the maths. No mirror, no doll, no basement.
"""

import os
import sys

ENTRY_TEXT = (
    "The photograph from my grandmother's funeral shows a boy my age "
    "standing behind the mourners, smiling at the camera \u2014 and he "
    "has my face."
)

MAX_CHARS = 200


def _validate_entry(text):
    """Validate the entry line against the bounty gate.

    Returns a list of problems (empty means valid). The gate requires
    UTF-8 text of 1 to 200 characters, not only white space, a single
    sentence on a single line.
    """
    problems = []
    if not isinstance(text, str):
        return ["entry is not text"]
    if "\r" in text:
        problems.append("entry contains a carriage return")
    stripped = text.strip()
    if not stripped:
        problems.append("entry is empty or only white space")
    if text != stripped:
        problems.append("entry has leading or trailing white space")
    if "\n" in text:
        problems.append("entry spans more than one line")
    if len(text) > MAX_CHARS:
        problems.append(
            "entry is %d characters, over the %d-character limit"
            % (len(text), MAX_CHARS)
        )
    if len(text) < 1:
        problems.append("entry is empty")
    if text.count(".") != 1 or not text.endswith("."):
        problems.append("entry is not exactly one sentence ending in '.'")
    if "!" in text or "?" in text:
        problems.append("entry has a second sentence terminator ('!' or '?')")
    for ch in text:
        if ord(ch) < 0x20 and ch not in ("\t",):
            problems.append("entry contains a control character U+%04X" % ord(ch))
            break
    return problems


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    # Guard: never write into the repo directory. The grader sandbox
    # mounts the repo read-only, so writing there would crash the run;
    # refuse early instead of writing where the entry must not go.
    repo_dir = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
    out_real = os.path.realpath(out_dir)
    if out_real == repo_dir or out_real.startswith(repo_dir + os.sep):
        print(
            "error: MAKEFUN_OUTPUT_DIR must not be inside the repo directory",
            file=sys.stderr,
        )
        return 1

    problems = _validate_entry(ENTRY_TEXT)
    if problems:
        for problem in problems:
            print("invalid entry: " + problem, file=sys.stderr)
        return 1

    out_path = os.path.join(out_dir, "entry.txt")
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(ENTRY_TEXT + "\n")
    except OSError as exc:
        print("error: cannot write entry.txt: %s" % exc, file=sys.stderr)
        return 1

    # Read-back check: the file on disk must be exactly the validated line.
    try:
        with open(out_path, "r", encoding="utf-8", newline="") as f:
            written = f.read()
    except OSError as exc:
        print("error: cannot read back entry.txt: %s" % exc, file=sys.stderr)
        return 1
    if written != ENTRY_TEXT + "\n":
        print("error: read-back mismatch in entry.txt", file=sys.stderr)
        return 1
    if not written.endswith("\n") or written.endswith("\n\n"):
        print("error: entry.txt must end with exactly one newline", file=sys.stderr)
        return 1
    problems = _validate_entry(written[:-1])
    if problems:
        for problem in problems:
            print("invalid entry on read-back: " + problem, file=sys.stderr)
        return 1

    print("wrote %s (%d characters)" % (out_path, len(ENTRY_TEXT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
