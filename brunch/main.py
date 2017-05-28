#!/usr/bin/env python

import os
import os.path
import sys
import csv
import subprocess as sub

def isexec (fpath):
    if fpath == None: return False
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK) 

def which(program):
    fpath, fname = os.path.split(program)
    if fpath:
        if isexec (program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if isexec (exe_file):
                return exe_file
    return None

def parseArgs (argv):
    import argparse as a
    p = a.ArgumentParser (description='Benchmark Runner')
    
    p.add_argument ('--cpu', metavar='CPU',
                    type=int, help='CPU limit', default=60)
    p.add_argument ('--mem', metavar='MEM',
                    type=int, help='Memory limit (MB)', default=512)
    p.add_argument ('file', nargs='+', 
                    help='Benchmark files')
    p.add_argument ('--prefix', default='BRUNCH_STAT', 
                    help='Prefix for stats')
    p.add_argument ('--format', required=False, help='Fields',
                    default='base:Status:Cpu:File')
    p.add_argument ('--out', metavar='DIR', 
                    default="out", help='Output directory')
    p.add_argument ('--mode',
                    help='Mode of operation: interactive, sqsub',
                    choices=['interactive', 'sqsub'],
                     default='interactive')

    if '-h' in argv or '--help' in argv:
        p.print_help ()
        p.exit (0)
    
    try:
        k = argv.index ('--')
    except ValueError:
        p.error ("No '--' argument")
    
    args = p.parse_args (argv[:k])
    args.tool_args = argv[k+1:]

    # include date in output directory
    import datetime as dt
    dt = dt.datetime.now ().strftime ('%d_%m_%Y-t%H-%M-%S')
    args.out = '{out}.{dt}'.format (out=args.out, dt=dt)


    return args

def collectStats (stats, file):
    f = open (file, 'r')
    for line in f:
        if not line.startswith ('BRUNCH_STAT'): continue

        fld = line.split (' ')
        if len (fld) == 3:
            stats [fld[1]] = fld[2].strip ()
    f.close ()
    return stats

def logToolArgs (args_file, tool_args):
    with open (args_file, 'w') as output:
        output.write (' '.join (tool_args))
        output.write ('\n')
    
def statsHeader (stats_file, flds):
    with open (stats_file, 'w') as sf:
        writer = csv.writer (sf)
        writer.writerow (flds)

def statsLine (stats_file, fmt, stats):
    line = list()
    for fld in fmt:
        if fld in stats: line.append (str (stats [fld]))
        else: line.append (None)

    with open (stats_file, 'a') as sf:
        writer = csv.writer (sf)
        writer.writerow (line)

cpuTotal = 0.0

def submitJob (tool_args, f, out, cpu, mem):
    fmt_tool_args = [v.format(f=f) for v in tool_args]
    fmt_tool_args[0] = which (fmt_tool_args[0])
    base = os.path.basename (f)
    outfile = os.path.join (out, base + '.stdout')
    errfile = os.path.join (out, base + '.stderr')

    sqsub_args = ['sqsub', '-r', str(cpu/60), '--mpp={m}G'.format(m=(mem/1024)),
                  '-o', outfile, '-e', errfile]
    sqsub_args[0] = which (sqsub_args [0])
    sqsub_args.extend (fmt_tool_args)

    print ' '.join (sqsub_args)
    sub.check_call (sqsub_args)
    
def runTool (tool_args, f, out, cpu, mem, fmt):
    global cpuTotal
    import resource as r

    def set_limits ():
        if mem > 0:
            mem_bytes = mem * 1024 * 1024
            r.setrlimit (r.RLIMIT_AS, [mem_bytes, mem_bytes])
        if cpu > 0:
            r.setrlimit (r.RLIMIT_CPU, [cpu, cpu])

    fmt_tool_args = [v.format(f=f) for v in tool_args]
    fmt_tool_args[0] = which (fmt_tool_args[0])
    
    base = os.path.basename (f)
    outfile = os.path.join (out, base + '.stdout')
    errfile = os.path.join (out, base + '.stderr')
    
    
    p = sub.Popen (fmt_tool_args, 
                   stdout=open(outfile, 'w'), stderr=open(errfile, 'w'),
                   preexec_fn=set_limits)

    p.wait ()
    cpuUsage = r.getrusage (r.RUSAGE_CHILDREN).ru_utime

    stats = dict()
    stats['File'] = f
    stats['base'] = base
    stats['Status'] = p.returncode
    stats['Cpu'] = '{0:.2f}'.format (cpuUsage - cpuTotal)
    cpuTotal = cpuUsage
    
    stats = collectStats (stats, outfile)
    stats = collectStats (stats, errfile)
    statsLine (os.path.join (out, 'stats'), fmt, stats)

def main ():
    argv = sys.argv
    args = parseArgs (argv[1:])

    if not os.path.exists (args.out):
        os.mkdir (args.out)

    logToolArgs (os.path.join (args.out, 'tool_args'), args.tool_args)
    
    if args.mode <> 'sqsub':
        fmt = args.format.split (':')
        statsHeader (os.path.join (args.out, 'stats'), fmt)

    global cpuTotal
    import resource as r
    cpuTotal = r.getrusage (r.RUSAGE_CHILDREN).ru_utime    

    for f in args.file:
        if args.mode == 'sqsub':
            submitJob (args.tool_args, f, args.out,
                       cpu=args.cpu, mem=args.mem)
        else:
            runTool (args.tool_args, f, args.out,
                     cpu=args.cpu, 
                     mem=args.mem, 
                     fmt=fmt)
    return 0
if __name__ == '__main__':
    sys.exit (main ())
