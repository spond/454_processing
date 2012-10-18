import os, argparse, re, sys
import csv
import datetime, shutil, json
from datetime import time, date
#import xlsx
from os.path import join, splitext, isfile


def tupleToDate (tuple):
    dateRec = date (tuple[0],tuple[1],tuple[2])

    return dateRec.strftime ("%m%d%Y")


def main (cache_file):
    if os.path.exists(cache_file):
        with open (cache_file, "r") as fh:
            processed_fna = json.load (fh)
                      
    byID = {}
    
    total454 = 0
    
    for filename,file454 in processed_fna.items():
        if 'aiedrp_id' in file454:
            if file454['aiedrp_id'] not in byID:
                if file454 ['aiedrp_id'] is not None:
                    if 'tn93' in file454 and file454 ['tn93'] is not None and file454['tn93'][1] > 1000:
                        total454+=1
                        byID[file454['aiedrp_id']] = [tupleToDate (file454 ['sample_date'])]
            else:
                if file454 ['aiedrp_id'] is not None:
                    if 'tn93' in file454 and file454 ['tn93'] is not None and file454['tn93'][1] > 1000:
                        total454+=1
                        date2 = tupleToDate (file454 ['sample_date'])
                        if date2 not in byID[file454['aiedrp_id']]:
                            byID[file454['aiedrp_id']].append(date2)
               
    print (len(byID), total454)
    print (byID)
    
    return 0

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Tabulate 454 results'
    )

    parser.add_argument(
        '-c', '--cache',
        metavar='JSON',
        type=str,
        help='the file which contains the .json cache file',
        required = True
    )
        
    args = None
    retcode = -1
    args = parser.parse_args()
        
    retcode = main(args.cache)
    
    sys.exit(retcode)


