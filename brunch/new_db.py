#!/usr/bin/env python3

import sys
import sqlite3 as sql

class NewDb (object):

    def __init__ (self):
        self.name = 'new_db'
        self.help = 'Create new sqlite database'
        
    def create_num_table (self, db):
        ctable = """
    drop table if exists nums;
    drop index if exists nums_num;
    create table if not exists nums (num integer);
    create unique index if not exists nums_num on nums(num);
    """
        curs = db.cursor ()
        curs.executescript (ctable)

        ivalue = "insert into nums values (?);"
        curs.executemany (ivalue, [ (i, ) for i in range (1, 120, 1)])

        db.commit ()
        
    def mk_arg_parser (self, ap):
        ap.add_argument ('--db', dest='db',
                         metavar='FILE', help='Database location',
                         default='results.sqlite')
        return ap

    def run (self, args):
        db = sql.connect (args.db)
        self.create_num_table (db)
        db.close ()
        
    def main (self, argv):
        import argparse
        
        ap = argparse.ArgumentParser (prog=self.name, description=self.help)
        ap = self.mk_arg_parser (ap)

        args = ap.parse_args (argv)
        return self.run (args)
    
def main ():
    cmd = NewDb ()
    return cmd.main (sys.argv[1:])

if __name__ == '__main__':
    sys.exit (main ())
