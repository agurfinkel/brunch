### Log scrabber for Spacer
import sys
import os
import os.path
import re

import pandas

class PrefixFilter (object):
    def __init__ (self, pref):
        self.pref = pref
        
    def __contains__ (self, item):
        for p in self.pref:
            if item.startswith (p):
                return True

        return False
    
class ReMatch (object):
    def __init__ (self, regex, filt):
        self._re = re.compile (regex)
        self._filter = filt
        
    def match (self, line):
        res = self._re.match (line)
        if res is None: return None

        fld = res.group ('fld')
        # optionally filter out
        if self._filter is not None and fld not in self._filter:
            return None
        
        return (fld, res.group ('val'))

        
class ExactMatch (object):
    def __init__ (self, name, values):
        self.field = name
        self._values = values

    def match (self, line):
        for v in self._values:
            if v == line:
                return (self.field, v)
        return None
    
class ExitStatus (object):
    def __init__ (self):
        self.field = 'status'
        
    def match (self, line):
        if not line.startswith ('exit status: '):
            return None

        l = line[len('exit status: '):]
        value = int (l.strip ())
        return (self.field, value)
    
class CpuTime (object):
    def __init__ (self):
        self.field = 'cpu'

    def match (self, line):
        try:
            if not line.startswith ('cpu time: '):
                return None
            return (self.field, int (line.split()[2][:-1]))
        except:
            return None

def _escape (s):
    s = s.replace ('.', '_').replace ('-', '_')
    return s

class LogScrabber (object):
    def __init__ (self, name='LogScrabber', help='Scrabbs Spacer logs'):
        self.name = name
        self.help = help
        self.store = list()

        self.matchers = list ()
        self.__init_matchers ()

    def __init_matchers (self):
        self.matchers.append (ExitStatus ())
        self.matchers.append (CpuTime ())
        self.matchers.append (ExactMatch ('result', ['sat','unsat']))
        regex = ':(?P<fld>[a-zA-Z0-9_.-]+)\s+(?P<val>\d+(:?[.]\d+)?)'
        flt = PrefixFilter (['SPACER-', 'time', 'virtual_solver'])
        reMatch = ReMatch(regex=regex, filt=flt)
        self.matchers.append (reMatch)

    def mk_arg_parser (self, ap):
        ap.add_argument ('-o', dest='out_file',
                        metavar='FILE', help='Output file name',
                         default='out.csv')
        ap.add_argument ('in_files',  metavar='FILE',
                         help='Input file', nargs='+')
        
        return ap
    
    def add_record(self, index, field, value):
        field = _escape (field)
        rec = {'index': index, 'field': field, 'value': value}
        self.store.append (rec)
        
    def _scrab (self, name, line):
        for m in self.matchers:
            try:
                res = m.match (line)
                if res is not None:
                    self.add_record (name, res[0], res[1])
            except:
                print '[WARNING]: exception for:', line
                print "Unexpected error:", sys.exc_info()
    def _processFile (self, fname):
        '''process a single file'''
        
        base_name = os.path.basename (fname)
        name, _ext = os.path.splitext (base_name)
        with open (fname) as input:
            for line in input:
                self._scrab (name, line.strip ())

    def _processDir (self, root):
        '''Recursively process all files in the root directory'''
        for root, dirs, files in os.walk(root):
            for name in files:
                if name.endswith ('.stdout') or name.endswith ('.stderr'):
                    self._processFile (os.path.join(root, name))        
    
    def _process (self, name):
        if os.path.isfile (name):
            self._processFile (name)
        elif os.path.isdir (name):
            self._processDir (name)
        else:
            assert False
            
    def _writeTable (self, out):
        df = pandas.DataFrame (self.store)
        
        def _last_fn (a):
            return a.get_value (a.first_valid_index ())

        ## use pivot_table with aggfunc that picks the first value
        df = df.pivot_table (index='index',
                             columns='field',
                             values='value',
                             aggfunc = _last_fn)
        df.to_csv (out)
    def run (self, args=None):
        for f in args.in_files:
            self._process (f)

        self._writeTable (args.out_file)
        
        return 0

    def main (self, argv):
        import argparse
        
        ap = argparse.ArgumentParser (prog=self.name, description=self.help)
        ap = self.mk_arg_parser (ap)

        args = ap.parse_args (argv)
        return self.run (args)
    
def main ():
    cmd = LogScrabber ()
    return cmd.main (sys.argv[1:])

if __name__ == '__main__':
    sys.exit (main ())
