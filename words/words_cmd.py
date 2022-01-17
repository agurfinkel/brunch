#! /usr/bin/env python3

# Suggest name to z3 binary based on it its sha

import sys
import argparse

from . import common


class WordsCmd(object):

    def __init__(self):
        self._name = 'words'
        self._help = 'Returns random words'

    def mk_arg_parser(self, ap):
        ap.add_argument('--noun', '-n', help='Noun', action='store_true')
        ap.add_argument('--length',
                        '-l',
                        type=int,
                        metavar='LENGTH',
                        default=None)
        ap.add_argument('--adj', '-a', help='Adjective', action='store_true')
        ap.add_argument('--seed', '-s', type=str, metavar='SEED', default=None)
        return ap

    def run(self, args=None):

        # pick a noun if adjective is not selected
        if not args.adj:
            get_a_word_fn = common.get_a_noun
        else:
            get_a_word_fn = common.get_an_adjective

        word = get_a_word_fn(length=args.length, seed=args.seed, bound='atmost')
        print(word)
        return 0

    def main(self, argv):
        ap = argparse.ArgumentParser(prog=self._name, description=self._help)
        ap = self.mk_arg_parser(ap)
        args = ap.parse_args(argv)
        return self.run(args)


def main():
    cmd = WordsCmd()
    return cmd.main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
