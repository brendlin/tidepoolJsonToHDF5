#!/usr/bin/env python3

import numpy as np
import pandas as pd

def main(args) :

    print(args)
    return

if __name__ == '__main__' :
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--summary' ,action='store_true',default=False,help='Make summary root file')
    parser.add_argument('--ndetailed',type=int,default=4,help='Number of weeks of detail (4)')
    parser.add_argument('--outname'  ,default='output.root',help='Output file name')
    parser.add_argument('--datadir'  ,default='data',help='Data directory')

    main(parser.parse_args())
