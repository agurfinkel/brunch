#! /usr/bin/env python3

# Suggest name to z3 binary based on it its sha

import sys
import words
import subprocess
import argparse
import os.path


class Z3Namer(object):

    def __init__(self):
        self._name = 'name_z3'
        self._help = 'Name for z3 binary'

    def mk_arg_parser(self, ap):
        ap.add_argument('z3bin',
                        metavar='Z3_BIN',
                        help='Full path to z3 binary')
        return ap

    def run(self, args=None):
        z3bin = args.z3bin
        z3ver_str = subprocess.check_output(f'{z3bin} --version',
                                            shell=True,
                                            encoding='utf-8')
        z3ver = z3ver_str.split()
        git_sha = z3ver[9]
        short_git_sha = git_sha[0:7]
        noun = words.get_a_noun(length=5, bound='atmost', seed=git_sha)
        z3bin_base = os.path.basename(z3bin)

        print(f'{z3bin_base}-{noun}-{short_git_sha}')
        return 0

    def main(self, argv):
        ap = argparse.ArgumentParser(prog=self._name, description=self._help)
        ap = self.mk_arg_parser(ap)
        args = ap.parse_args(argv)
        return self.run(args)


def main():
    cmd = Z3Namer()
    return cmd.main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
