#! /usr/bin/env python3

# Suggest name to z3 binary based on it its sha

import sys
import words
import subprocess
import argparse
import os.path
import shutil


class Z3Namer(object):

    def __init__(self):
        self._name = 'name_z3'
        self._help = 'Name for z3 binary'

    def mk_arg_parser(self, ap):
        ap.add_argument('z3bin',
                        metavar='Z3_BIN',
                        help='Full path to z3 binary')
        ap.add_argument('-o',
                        type=str,
                        metavar="DIR",
                        help='Copies renamed binary to given directory',
                        default=None)
        return ap

    def run(self, args=None):
        copy_mode = args.o is not None
        out_dir = args.o

        if copy_mode and not os.path.isdir(out_dir):
            print(f"Error: '{out_dir}' is not a directory", file=sys.stderr)
            return 1

        z3bin = args.z3bin
        z3ver_str = subprocess.check_output(f'{z3bin} --version',
                                            shell=True,
                                            encoding='utf-8')
        z3ver = z3ver_str.split()

        if len(z3ver) == 10:
            # z3 version with build hashcode
            git_sha = z3ver[9]
            short_git_sha = git_sha[0:7]
        else:
            # z3 release without build hashcode
            # use z3_version instead of the hashcode
            git_sha = z3ver[2].replace('.', '_')
            short_git_sha = git_sha

        noun = words.get_a_noun(length=5, bound='atmost', seed=git_sha)
        z3bin_base = os.path.basename(z3bin).replace('-', '_')

        z3_name = f'{z3bin_base}-{noun}-{short_git_sha}'
        if copy_mode:
            shutil.copy2(z3bin, os.path.join(out_dir, z3_name))
        else:
            print(z3_name)
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
