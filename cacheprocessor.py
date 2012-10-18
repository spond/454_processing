import os, argparse, re, sys, xlrd3
import csv
import datetime, shutil, json
#import xlsx
from os.path import join, splitext, isfile
from datetime import date, time
def tupleToDate (tuple):
    dateRec = date (tuple[0],tuple[1],tuple[2])
    return dateRec.strftime ("%m%d%Y")
    
def compressAIEDRPID (id):
    return id.replace ('-', '')
    
def main (qtype,qvalue,cache_file):
   
    with open (cache_file, "r") as fh:
        file_cache = json.load (fh)

    result = []
    print (qvalue)
    if qtype == 'AEH':
        return [  file_cache[a454]['codon_alignment'] for a454 in file_cache if 'aiedrp_id' in file_cache[a454] and file_cache[a454]['aiedrp_id'] is not None and 'codon_alignment' in file_cache[a454] and compressAIEDRPID(file_cache[a454]['aiedrp_id']) + '|' + tupleToDate (file_cache[a454]['sample_date']) == qvalue]
        #return [ file_cache[a454]['codon_alignment'] for a454 in file_cache if 'aiedrp_id' in file_cache[a454] and file_cache[a454]['aiedrp_id'] is not None and 'codon_alignment' in file_cache[a454]]
#and file_cache[a454]['aiedrp_id'] + '|' + tupleToDate (file_cache[a454]['sample_date']) == qvalue
    return None

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='read cache file and convert various IDs'
    )
    parser.add_argument(
        '-t', '--type',
        metavar='type',
        type=str,
        choices = ('AEH', 'FILENAME', 'ID'),
        help='the directory to scan',
        required = True
    )
    parser.add_argument(
        '-v', '--value',
        metavar='value',
        type=str,
        help='the directory to scan',
        required = True
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
        
    print (main(args.type, args.value, args.cache))
    
    


