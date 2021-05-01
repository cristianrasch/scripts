#!/usr/bin/env python3

import re
import unittest
from pathlib import Path


KEY_RE = re.compile(r'([A-Z]\w*)\s*=\s*(["\'])?.*?\2?', re.I)


def diff_between_env_files(source: Path, target: Path) -> set:
    if not source.is_file() or not target.is_file():
        return set([])

    return extract_keys_from(source) - extract_keys_from(target)


def extract_keys_from(file: Path) -> set:
    keys = set([])
    with file.open() as f:
        for line in f:
            if match := KEY_RE.match(line):
                keys.add(match.group(1))

    return keys


class TestEnvDiff(unittest.TestCase):
    def setUp(self):
        self.source = Path('source.env')
        with self.source.open('w') as f:
            f.write('KEY_ONE = ONE\n')
            f.write('KEY_2="VALUE TWO"\n')
            f.write("KEY_THREE='VALUE THREE'\n")
            f.write('KEY_FOUR=\n')

        self.target = Path('target.env')
        with self.target.open('w') as f:
            f.write('KEY_ONE=\n')
            f.write("KEY_2='VALUE TWO'\n")
            f.write('KEY_THREE="VALUE THREE"\n')
            f.write('# KEY_FOUR=FOUR\n')
            f.write('KEY_FIVE=\n')

    def tearDown(self):
        self.source.unlink()
        self.target.unlink()

    def test_key_diff(self):
        self.assertEqual(diff_between_env_files(self.source, self.target), {'KEY_FOUR'})


if __name__ == '__main__':
    import argparse
    import sys

    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        sys.argv.pop(1)
        unittest.main()

    parser = argparse.ArgumentParser(description='Compare .env files.')
    parser.add_argument('source', type=Path, help='the source file')
    parser.add_argument('target', type=Path, help='the target file')
    args = parser.parse_args()

    files = [args.source, args.target]
    for file in files:
        if not file.is_file():
            sys.exit(f"'{file}' is not a file or is otherwise inaccessible")

    if diffs := diff_between_env_files(args.source, args.target):
        for diff in diffs:
            print(diff)
        sys.exit(1)
