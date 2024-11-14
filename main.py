from sql_import import *
from sql_import_ismuni import *

import sys

fileIn = None
fileOut = None
outType = None
sqlDb = None

def printHelp():
    print("Command Line IS MUNI QDEFX 2 SQL Data Importer Utility\n" \
          "\n" \
          "Example usage:\n" \
          "\t python.exe main.py -db cms -f 10_uvod.qdefx\n" \
         )

if __name__ == '__main__':
    for i, arg, in enumerate(sys.argv):
        if arg == '-h':
            printHelp()
            exit()
        elif arg == '-f':
            fileIn = sys.argv[i+1]
        elif arg == '-db':
            sqlDb = sys.argv[i+1]
        else:
            continue

    if fileOut is None:
        fileOut = fileIn.rsplit('.', maxsplit=1)[0]

    im = sql_import_ismuni(sqlDb, fileIn, fileOut)
    
