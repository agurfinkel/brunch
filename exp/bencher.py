#! /usr/bin/env python3

# Suggest name to z3 binary based on it its sha

import sys
import words
import subprocess
import argparse
import os.path
import shutil

from pathlib import Path

import yaml


class Bencher(object):

    def __init__(self):
        self._name = 'bencher'
        self._help = 'Make benchmark direcotry'

    def mk_arg_parser(self, ap):
        ap.add_argument('--suffix',
                        '-s',
                        metavar='EXT',
                        type=str,
                        default='smt2',
                        required=True,
                        help='File extension')
        ap.add_argument('--prefix',
                        '-p',
                        metavar='PREF',
                        required='True',
                        help='Prefix to assign')
        ap.add_argument('--out',
                        '-o',
                        type=str,
                        metavar="DIR",
                        help='Output directory',
                        required=True)
        ap.add_argument('files', nargs='+')
        ap.add_argument(
        '--mv',
        action='store_true',
            help='Move (instead of copy) benchmarks into new location')
        ap.add_argument('--verbose', '-v', action='store_true')
        ap.add_argument('--dry-run', action='store_true')
        return ap

    def run(self, args=None):

        num_files = len(args.files)
        num_fmt = '{idx:0' + str(len(str(num_files))) + '}'

        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)

        prefix = args.prefix
        suffix = args.suffix

        # pick an action to apply to each file
        if args.dry_run:
            def _dry_run_action(src, dst):
                pass
            file_action = _dry_run_action
        elif args.mv:
            file_action = shutil.move
        else:
            file_action = shutil.copy2

        inverse = dict()
        for id, src in enumerate(args.files):
            idx_str = num_fmt.format(idx=id)

            dst_name = f'{prefix}-{idx_str}.{suffix}'
            dst = out_dir / dst_name
            if (args.verbose):
                print(f'{src} --> {dst}')
            file_action(src, dst)

            inverse[dst_name] = src

        with open(out_dir / 'inverse.yaml', 'w') as inverse_file:
            yaml.dump(inverse, inverse_file)

        return 0

    def main(self, argv):
        ap = argparse.ArgumentParser(prog=self._name, description=self._help)
        ap = self.mk_arg_parser(ap)
        args = ap.parse_args(argv)
        return self.run(args)


def main():
    cmd = Bencher()
    return cmd.main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
