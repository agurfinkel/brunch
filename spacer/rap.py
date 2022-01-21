#! /usr/bin/env python3

from pathlib import Path
import pandas as pd
import sys
import argparse


class RapSheet:

    def __init__(self, path):
        _path = Path(path).absolute()
        if _path.is_dir():
            self.dir = _path
            self.stats_file = _path / 'stats.csv'
        elif _path.is_file():
            self.dir = _path.parent
            self.stats_file = _path
        else:
            assert False

        # if name looks like expected, extract descriptive name
        # ow, use directory as the name
        _name = self.dir.name.split('.')
        if len(_name) >= 4:
            self.name = _name[-2]
        else:
            self.name = self.dir.name

        # load csv file into data frame
        self.df = self._load_stats()

    def _load_stats(self):
        _df = pd.read_csv(self.stats_file)

        # push unknown time to max
        max_time = int(_df.time.max() + 50)
        _df.time.fillna(value=max_time, inplace=True)

        # other data cleaning goes here

        return _df

    def get_by_status(self):
        """Get DataFrame grouped by status."""
        return self.df[['index', 'status']].groupby('status').count()

    def compare_status(self, other, join_on='index'):
        _mrg = self.df[[join_on, 'status'
                        ]].merge(other.df[[join_on, 'status']],
                                 on=join_on,
                                 suffixes=('_' + self.name, '_' + other.name))
        return _mrg.groupby([f'status_{self.name}',
                             f'status_{other.name}']).count()[[join_on]]

    def compare_time(self, other, join_on='index'):
        _mrg = self.df[[join_on, 'status', 'time'
                        ]].merge(other.df[[join_on, 'status', 'time']],
                                 on=join_on,
                                 suffixes=('_' + self.name, '_' + other.name))
        return _mrg.groupby([f'status_{self.name}', f'status_{other.name}'
                             ])[[f'time_{self.name}', f'time_{other.name}']]






class RapCmd(object):

    def __init__(self):
        self._name = 'rap'
        self._help = 'Describe statistics of a run'

    def mk_arg_parser(self, ap):
        ap.add_argument('exps', nargs='+',
                        help='Output directories for experiments')
        return ap

    def run(self, args=None):

        assert len(args.exps) <= 2

        rs = list()
        for exp in args.exps:
            rs.append(RapSheet(exp))
            name = rs[-1].name
            print(f'Stats for {name}:')
            print(rs[-1].df.time.describe())
            print(rs[-1].get_by_status())
            print()

        if len(rs) == 2:
            print(rs[0].compare_status(rs[1]))

        return 0

    def main(self, argv):
        ap = argparse.ArgumentParser(prog=self._name, description=self._help)
        ap = self.mk_arg_parser(ap)
        args = ap.parse_args(argv)
        return self.run(args)


def main():
    cmd = RapCmd()
    return cmd.main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
