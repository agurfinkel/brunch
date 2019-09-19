#!/usr/bin/evn python3

import sys
import csv
import sqlite3 as sql

from optparse import OptionParser

class LoadTable (object):
    def __init__ (self):
        self.name = 'load_table'
        self.help = 'Create a table based on csv'
        self.fld_dict = { 'filename': 'file',
                          '#pass-ing' : 'pass_ing',
                          'index' : 'file'}

    def fld_name (self, fld):
        if fld in self.fld_dict: return self.fld_dict [fld]
        return fld.replace ('.', '_').replace (' ', '_')

    def get_type (self, v):
        if v == None: return None
        if v == '': return None
        try:
            int (v)
            return 'integer'
        except ValueError:
            try:
                float (v)
                return 'real'
            except ValueError:
                return 'text'
    
    def deduce_types (self, reader):
        types = list(map (self.get_type, next (reader)))
        def merge_type (t1, t2):
            if t1 == 'text' or t2 == 'text': return 'text'
            elif t1 == 'real' or t2 == 'real': return 'real'
            elif t1 == 'integer' or t2 == 'integer': return 'integer'
            else: 
                assert t1 == t2 == None
                return None

        for row in reader:
            types = [merge_type (t, self.get_type (i)) for (t, i) in zip (types, row)]
        return types
    
    def normalize_fld_names (self, fld):
        flds = dict ()
        for i in range (len (fld)):
            if flds.get (fld [i]) is not None:
                n = flds [fld [i]] 
                n = n + 1
                flds [fld [i]] = n
                # add index to fld name
                fld [i] = fld[i] + str(n)
            else:
                flds [fld [i]] = 0
        return fld
    
    def create_ufo_table (self, db, table, flds, types, pk):
        sql_fld_names = list(map (self.fld_name, flds))
        sql_fld_types = [x == None and 'text' or x for x in types]
        sql_pk = self.fld_name (pk)

        sql_col_def = ', '.join ([' '.join ((x, y)) 
                                for (x,y) in zip (sql_fld_names, sql_fld_types)])

        print("Creating table '{table}'".format(table=table))

        ctable = """
    drop table if exists {name};
    drop index if exists {name}_total;
    drop index if exists {name}_{pk};
    create	table if not exists {name}( {cols} );

    create unique index if not exists {name}_{pk} on {name}({pk});

    """
        ctable = ctable.format (name=table, cols=sql_col_def, pk=sql_pk)
        db.cursor ().executescript (ctable);
        db.commit ()
    
    def load_ufo_csv (self, csvfile, db, table, pk, create_table = False):
        print("Loading file '{name}'".format (name=csvfile))
        c = db.cursor ()
        with open (csvfile, 'rb') as infile:
            reader = csv.reader (infile, dialect='excel')
            # read the header
            fld = next (reader)

            fld = self.normalize_fld_names (fld)
            col = ', '.join (['?' for i in fld])
            ivalue = "insert into {name} values ({col});"
            ivalue = ivalue.format (name=table, col=col)

            if create_table: 
                types = self.deduce_types (reader)
                self.create_ufo_table (db, table, fld, types, pk)

                ## reset everything to the beginning
                infile.seek (0)
                reader = csv.reader (infile, dialect='excel')
                x = next (reader)

            c.executemany (ivalue, reader)
        db.commit ()
    
    def create_solved_views (self, db, table):
        print("Creating solved views")
        view = """
    create view if not exists {name}_solved as select num, count(*) as solved from {name}, nums where (res is 'SAFE' or res is 'CEX') and total <= num group by num order by num;

    create view if not exists {name}_solved_safe as select num, count(*) as solved from {name}, nums where (res is 'SAFE') and total <= num group by num order by num;

    create view if not exists {name}_solved_cex as select num, count(*) as solved from {name}, nums where (res is 'CEX') and total <= num group by num order by num;

    """.format (name=table)

        db.cursor ().executescript (view)
        db.commit ()
        
    def mk_arg_parser (self, ap):
        ap.add_argument ('-t', '--table', dest='table',
                         help='Table name',required=True)
        ap.add_argument ('--db', dest='db',
                         metavar='FILE', help='Database location',
                         default='results.sqlite')
        ap.add_argument ('--use-existing', dest='existing',
                         default=False, help='Do not re-create the table',
                         action='store_true')
        ap.add_argument ('--pk', default='file', help='Primary key column')
        ap.add_argument ('in_files', nargs='+', help='CSV files')

        return ap

    def run (self, args):
        db = sql.connect (args.db)
        create_table = not args.existing
        for file in args.in_files:
            self.load_ufo_csv (file, db, args.table, args.pk, create_table)
            create_table = False

        #    create_solved_views (db, opt.table)

        db.close ()

        
    def main (self, argv):
        import argparse
        
        ap = argparse.ArgumentParser (prog=self.name, description=self.help)
        ap = self.mk_arg_parser (ap)

        args = ap.parse_args (argv)
        return self.run (args)
    
def main ():
    cmd = LoadTable ()
    return cmd.main (sys.argv[1:])

if __name__ == "__main__":
    sys.exit (main ())
