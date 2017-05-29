#!/usr/bin/python

import sys
import sqlite3 as sql
from optparse import OptionParser


def create_num_table (db):
    ctable = """
drop table if exists nums;
drop index if exists nums_num;
create table if not exists nums (num integer);
create unique index if not exists nums_num on nums(num);
"""
    curs = db.cursor ()
    curs.executescript (ctable)

    ivalue = "insert into nums values (?);"
    curs.executemany (ivalue, [ (i, ) for i in xrange (1, 120, 1)])

    db.commit ()

def parseOpt ():
    parser = OptionParser ()
    parser.add_option ("--db", dest="db", 
                       help="Database location",
                       default="results.db")
    (opt, args) = parser.parse_args ()
    if not len (args) == 0:
        parser.error ("Unknown arguments")

    return opt
    

def main ():
    opt = parseOpt ()

    db = sql.connect (opt.db)
    create_num_table (db)
    db.close ()


if __name__ == "__main__":
    sys.exit (main ())
