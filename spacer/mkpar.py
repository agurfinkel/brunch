#! /usr/bin/env python3

# Name for experiments directory

import sys
import argparse
import os.path
import string
import importlib.resources
import os


class MkPar(object):

    def __init__(self):
        self._name = 'mkpar'
        self._help = 'Create script to run parallel experiments'

    def _mk_arg_parser(self, ap):
        ap.add_argument('--out',
                        '-o',
                        metavar='DIR',
                        help='Output directory',
                        default="./run")
        ap.add_argument('--parallel',
                        metavar='FILE',
                        help='Location of GNU Parallel',
                        default='/usr/local/bin/parallel')
        ap.add_argument('--jobs',
                        '-j',
                        metavar='INT',
                        type=int,
                        help='Number of jobs to run in parallel',
                        default=8)
        ap.add_argument('--exp',
                        metavar='DIR',
                        help='Output directory for experiments',
                        default='./out')

        ap.add_argument('tool', metavar='TOOL', help='Path to tool script')
        ap.add_argument('idx', metavar='BENCHMARKS', help='Benchmark index file')
        return ap

    def run(self, args=None):

        tool = os.path.abspath(args.tool)
        idx = os.path.abspath(args.idx)

        tool_name = os.path.basename(tool)
        tool_name = os.path.splitext(tool_name)[0]
        tool_name = tool_name.split('-')
        assert len(tool_name) == 2

        tool_name, opts_name = tool_name[0], tool_name[1]

        # == Create script file ==

        # read template
        resource = importlib.resources.files(
            __package__) / "run-tool-opts.sh.in"
        with resource.open('r') as f:
            body = string.Template(f.read())

    # write out file
        out_file = os.path.join(args.out, f'run-{tool_name}-{opts_name}.sh')
        print(f'Writing {out_file}')
        with open(out_file, 'w', encoding='utf-8') as f:
            # substitute template
            f.write(
                body.substitute(tool=tool,
                                tool_name=tool_name,
                                opts_name=opts_name,
                                out_dir=os.path.abspath(args.exp),
                                parallel=os.path.abspath(args.parallel),
                                jobs=args.jobs,
                                idx=idx))

        # make executable by owner and group
        os.chmod(out_file, 0o770)

    def main(self, argv):
        ap = argparse.ArgumentParser(prog=self._name, description=self._help)
        ap = self._mk_arg_parser(ap)
        args = ap.parse_args(argv)
        return self.run(args)


if __name__ == '__main__':
    cmd = MkPar()
    sys.exit(cmd.main(sys.argv[1:]))
