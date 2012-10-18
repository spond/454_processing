import os, argparse, re, sys
import subprocess, itertools, time
import shutil, json
from os.path import join, splitext, isfile
from datetime import date, time

tn93xtract = re.compile ('Found ([0-9]+) links among ([0-9]+) pairwise comparisons')

def tupleToDate (tuple):
    dateRec = date (tuple[0],tuple[1],tuple[2])
    return dateRec.strftime ("%m%d%Y")
    
def compressAIEDRPID (id):
    return id.replace ('-', '')
    
def reportMI (row):
    if 'mi' in row and row['mi'] is not None:
        return row['mi']
    return ''

def main (cache_file_pair, cache, bulk):  
    missing_names = set()
    missing_dir   = {}
    unique_ids    = set ()
    reported_pairs = set ()
    unmatched      = set ()
    if os.path.exists(cache_file_pair):
        with open (cache_file_pair, "r") as fh:
            previous_pair_cache = json.load (fh)
    else:
        return 1

    if os.path.exists(cache):
        with open (cache, "r") as fh:
            cache = json.load (fh)
    else:
        return 1
        
    with open (bulk, "r") as fh:
        bulk = json.load (fh)

    print ("ID1,ID2,Distance")

    for key,value in previous_pair_cache.items():
        if value is not None:
            if value[0] * 20 > value [1]:
                file1, file2 =  key.split("|")
                for f in [file1,file2]:
                    if f not in cache:
                        dirtag = '/'.join(f.split ('/')[0:-1])
                        if dirtag in missing_dir:
                            missing_dir[dirtag] += 1 
                        else:
                            missing_dir[dirtag] = 1
                        missing_names.add (f)
                        
                if file1 in cache and file2 in cache:     
                    if cache[file1]['aiedrp_id'] is not None and cache[file2]['aiedrp_id'] is not None and cache[file1]['aiedrp_id'] != cache[file2]['aiedrp_id']:
                        #print (dir(tm1))
                        n1 = compressAIEDRPID(cache[file1]['aiedrp_id'])
                        n2 = compressAIEDRPID(cache[file2]['aiedrp_id'])
                        for n in [n1,n2]:
                            if n not in bulk and n not in unmatched:
                                #print (n)
                                unmatched.add (n)
                            
                        unique_ids.add (n1)
                        unique_ids.add (n2)
                        pair_tag = n1 + "|" + n2   if n1 < n2 else n2 + "|" + n1
                        if pair_tag not in reported_pairs:
                        	reported_pairs.add (pair_tag)
                        	count_tags = "%d:%d" % (value[0], value[1])
                        	
                        	print ("%s|%s|%s|%s,%s|%s|%s|%s,%f"% (n1,tupleToDate(cache[file1]['sample_date']),count_tags,reportMI(cache[file1]),n2,tupleToDate(cache[file2]['sample_date']),count_tags,reportMI(cache[file1]),0.01))
 
    '''for n in missing_names:
        print (n)
        
    print (missing_dir)
    '''
    
    return 0

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='scan the directory of 454 files and process them'
    )
    parser.add_argument(
        '-p', '--paircache',
        metavar='JSON_PAIR',
        type=str,
        help='the file which contains the .json cache for pairwise comparisons files',
        required = True
    )
    parser.add_argument(
        '-c', '--cache',
        metavar='JSON_PAIR',
        type=str,
        help='the file which contains the .json mapping filenames to other info',
        required = True
    )
    parser.add_argument(
        '-b', '--bulk',
        metavar='BULK_JSON',
        type=str,
        help='the file which contains the .json list of all seq.ids in the bulk database',
        required = True
    )
    args = None
    retcode = -1
    args = parser.parse_args()
        
    retcode = main(args.paircache, args.cache, args.bulk)
    
    sys.exit(retcode)


