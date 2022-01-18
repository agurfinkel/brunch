#! /usr/bin/env python3

# Name for experiments directory

import sys
import words
import argparse
import os.path
from datetime import datetime
import platform


class ExpNamer(object):

    def __init__(self):
        self._name = 'exp_name'
        self._help = 'Name experiment'

    def mk_arg_parser(self, ap):
        ap.add_argument('idx',
                        metavar='FILE',
                        help='Index of benchmarks for this experiment')
        return ap

    def run(self, args=None):
        idx = os.path.splitext(os.path.basename(args.idx))[0]
        date = datetime.now().strftime('%d_%m_%Y-t%H-%M-%S')
        noun = words.get_a_noun(length=7, bound='atmost', seed=date)
        noun = noun.lower()
        node = platform.node().split('.')[0]

        print(f"{idx}.{node}.{noun}.{date}")

    def main(self, argv):
        ap = argparse.ArgumentParser(prog=self._name, description=self._help)
        ap = self.mk_arg_parser(ap)
        args = ap.parse_args(argv)
        return self.run(args)


def main():
    cmd = ExpNamer()
    return cmd.main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
