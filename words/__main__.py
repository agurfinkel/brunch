import sys

from . import words_cmd

cmd = words_cmd.WordsCmd()
ret = cmd.main(sys.argv[1:])
sys.exit(ret)
