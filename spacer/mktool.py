#! /usr/bin/env python3

# Name for experiments directory

import sys
import argparse
import os.path
import string
import importlib.resources
import os

from . import yama


class MkTool(object):

    def __init__(self):
        self._name = 'mktool'
        self._help = 'Create script to run a tool'

    def mk_arg_parser(self, ap):
        ap.add_argument('z3bin', metavar='FILE', help='Path to Z3 binary')
        ap.add_argument('yaml', metavar='CONF', help='Configuration file')
        ap.add_argument('--out',
                        '-o',
                        metavar='DIR',
                        help='Output directory',
                        default="./run")
        ap.add_argument('--print',
                        help='Print command instead of creating a script',
                        action='store_true')
        return ap

    def run(self, args=None):

        z3bin = os.path.abspath(args.z3bin)
        with open(args.yaml, 'r', encoding='utf-8') as f:
            cli = yama.z3_yaml_to_cli(f.read())

        opts = ' '.join(cli)
        if args.print:
            print(f"{z3bin} {opts}")
            return 0

        # read template

        resource = importlib.resources.files(__package__) / "tool-opts.sh.in"
        with resource.open('r') as f:
            body = string.Template(f.read())

        # /PATH/z3-cat-a94304.exe --> cat
        tool_name = os.path.basename(z3bin)
        tool_name = os.path.splitext(tool_name)[0]
        tool_name = tool_name.split('-')[1]

        # /PATH/z3-high.conf --> high
        opts_name = os.path.basename(args.yaml)
        opts_name = os.path.splitext(opts_name)[0]
        opts_name = opts_name.split('-')[1]

        # write out file
        out_file = os.path.join(args.out, f'{tool_name}-{opts_name}.sh')
        print(f'Writing {out_file}')
        with open(out_file, 'w', encoding='utf-8') as f:
            # substitute template
            f.write(body.substitute(tool=z3bin, opts=opts))

        # make executable by owner and group
        os.chmod(out_file, 0o770)

    def main(self, argv):
        ap = argparse.ArgumentParser(prog=self._name, description=self._help)
        ap = self.mk_arg_parser(ap)
        args = ap.parse_args(argv)
        return self.run(args)


def main():
    cmd = MkTool()
    return cmd.main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
