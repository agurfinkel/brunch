#! /usr/bin/env python3

### Log scrabber for Spacer

import sys
import os
import os.path
import re
import pandas


class PrefixFilter(object):

    def __init__(self, pref):
        self.pref = pref

    def __contains__(self, item):
        for p in self.pref:
            if item.startswith(p):
                return True

        return False


class ReMatch(object):

    def __init__(self, regex, filt=None, field=None):
        self._re = re.compile(regex)
        self._filter = filt
        self._field = field

    def match(self, line):
        res = self._re.match(line)
        if res is None: return None

        if self._field is None:
            fld = res.group('fld')
        else:
            fld = self._field

        # optionally filter out
        if self._filter is not None and fld not in self._filter:
            return None

        return (fld, res.group('val'))


class ExactMatch(object):

    def __init__(self, name, values):
        self.field = name
        self._values = values

    def match(self, line):
        for v in self._values:
            if v == line:
                return (self.field, v)
        return None


class ErrorMatch(object):

    def __init__(self, name='error'):
        self.field = name

    def match(self, line):
        if line.startswith('(error'):
            return (self.field, '1')
        return None


class MemoryExcMatch(object):

    def __init__(self, name):
        self.field = name

    def match(self, line):
        if line.endswith('(error "out of memory")'):
            return (self.field, 'memout')
        return None


class ErrorExcMatch(object):

    def __init__(self, name):
        self.field = name

    def match(self, line):
        if line.endswith('unexpected end of quoted symbol")'):
            return (self.field, 'error_quote')
        elif line.endswith(
                'Invalid query argument, expected uinterpreted ' + \
                'function name, but argument is interpreted")'
        ):
            return (self.field, 'error_interp')
        return None


class ExitStatus(object):

    def __init__(self):
        self.field = 'status'

    def match(self, line):
        if line.startswith ('exit status: ') \
            or line.startswith ('Child status: '):
            value = int(line.split(':')[1].strip())
            return (self.field, value)

        if line.startswith('Child ended because it received signal'):
            value = int(line.split()[-2])
            return (self.field, value)

        return None


class PosixTime(object):
    """
    Time as produced by posix time (`time -p`)
    """

    def __init__(self):
        pass

    def match(self, line):
        try:
            if line.startswith('real') or \
               line.startswith('user') or \
               line.startswith('sys'):
                flds = line.split()
                if len(flds) == 2:
                    return (flds[0], float(flds[1]))
            return None
        except:
            return None


class CpuTime(object):

    def __init__(self):
        self.field = 'cpu'

    def match(self, line):
        try:
            if not line.startswith('cpu time: '):
                return None
            return (self.field, int(line.split()[2][:-1]))
        except:
            return None


class RealTime(object):

    def __init__(self):
        self.field = 'real_time'

    def match(self, line):
        """From runsolver."""
        try:
            if not line.startswith('Real time (s): '):
                return None
            val = float(line.split(':')[1].strip())
            return (self.field, "{:.2f}".format(val))
        except:
            return None


class MaxMemory(object):

    def __init__(self):
        self.field = 'max_memory'

    def match(self, line):
        """From runsolver."""
        try:
            if not line.startswith(
                    'Max. memory (cumulated for all children) (KiB): '):
                return None
            val = line.split(':')[1].strip()
            return (self.field, int(val))
        except:
            return None


class BrunchStat(object):

    def __init__(self):
        pass

    def match(self, line):
        """BRUNCH_STAT field value."""
        try:
            if not line.startswith('BRUNCH_STAT'):
                return None
            fields = line.split()
            return (fields[1], fields[2])
        except:
            return None


def _escape(s):
    s = s.replace('.', '_').replace('-', '_')
    return s


class LogScrabber(object):

    def __init__(self, name='LogScrabber', help='Scrabbs Spacer logs'):
        self.name = name
        self.help = help
        self.store = list()

        self.matchers = list()
        self.__init_matchers()

    def __init_matchers(self):
        self.matchers.append(
            ExactMatch('status', ['sat', 'unsat', 'timeout', 'unknown']))
        self.matchers.append(MemoryExcMatch('status'))
        self.matchers.append(ErrorExcMatch('status'))
        self.matchers.append(ExitStatus())
        self.matchers.append(ErrorMatch())
        self.matchers.append(CpuTime())
        self.matchers.append(RealTime())
        self.matchers.append(PosixTime())
        self.matchers.append(MaxMemory())
        self.matchers.append(BrunchStat())
        regex = r'[(]?:(?P<fld>[a-zA-Z0-9_.-]+)\s+(?P<val>\d+(:?[.]\d+)?)'
        flt = PrefixFilter(
            ['SPACER-', 'time', 'virtual_solver', 'memory', 'max-memory'])
        reMatch = ReMatch(regex=regex, filt=flt)
        self.matchers.append(reMatch)

        btor_time_regex = r'^\[.*\]\s+(?P<val>\d+(\.\d+)?)\s+seconds'
        btor_time = ReMatch(regex=btor_time_regex, field='btor_time')
        self.matchers.append(btor_time)

    def mk_arg_parser(self, ap):
        ap.add_argument('-o',
                        dest='out_file',
                        metavar='FILE',
                        help='Output file name',
                        default=None)
        ap.add_argument('in_files',
                        metavar='FILE',
                        help='Input file',
                        nargs='+')

        return ap

    def add_record(self, index, field, value):
        field = _escape(field)
        rec = {'index': index, 'field': field, 'value': value}
        self.store.append(rec)

    def _scrab(self, name, line):
        for m in self.matchers:
            try:
                res = m.match(line)
                if res is not None:
                    self.add_record(name, res[0], res[1])
            except:
                print('[WARNING]: exception for:', line)
                print("Unexpected error:", sys.exc_info())

    def _process_file(self, fname):
        '''process a single file'''

        base_name = os.path.basename(fname)

        if base_name.endswith('.smt2'):
            name = base_name
        else:
            name, _ext = os.path.splitext(base_name)

        with open(fname, errors='replace') as input:
            for line in input:
                self._scrab(name, line.strip())

    def _process_dir(self, root):
        '''Recursively process all files in the root directory'''
        for root, dirs, files in os.walk(root):
            for name in files:
                self._process_file(os.path.join(root, name))

    def _process(self, name):
        if os.path.isfile(name):
            self._process_file(name)
        elif os.path.isdir(name):
            self._process_dir(name)
        else:
            assert False

    def _write_table(self, out):
        df = pandas.DataFrame(self.store)

        def _last_fn(a):
            return a.at[a.last_valid_index()]

        if len(df) == 0:
            print('Error: no data')
            return None

        # use pivot_table with aggfunc that picks the first value
        df = df.pivot_table(index='index',
                            columns='field',
                            values='value',
                            aggfunc=_last_fn)
        df.to_csv(out)

    def run(self, args=None):

        # default output destination is file `stats.csv`
        # in input directory (if input dir is given)
        if args.out_file is None:
            args.out_file = 'stats.csv'
            if len(args.in_files) == 1:
                in_file = args.in_files[0]
                if os.path.isdir(in_file):
                    args.out_file = os.path.join(in_file, args.out_file)

        print('Creating', args.out_file, '...')

        for f in args.in_files:
            self._process(f)

        self._write_table(args.out_file)

        return 0

    def main(self, argv):
        import argparse

        ap = argparse.ArgumentParser(prog=self.name, description=self.help)
        ap = self.mk_arg_parser(ap)

        args = ap.parse_args(argv)
        return self.run(args)


def main():
    cmd = LogScrabber()
    return cmd.main(sys.argv[1:])


if __name__ == '__main__':

    sys.exit(main())
