import os, argparse, re, sys
import subprocess, itertools, time
import shutil, json
#import xlsx
from os.path import join, splitext, isfile

tn93xtract = re.compile ('Found ([0-9]+) links among ([0-9]+) pairwise comparisons')

def get_tn93_pair (path1, path2, n1,n2):
    print ("get_tn93_pair on %s-%s" % (n1,n2))
    try:
        output = subprocess.check_output (['/usr/bin/bpsh', '7', '/usr/local/bin/TN93dist', path1, 'COUNT', str(0.01), 'RESOLVE', 'CSV', '100', '0', path2], ) 
        #output = subprocess.check_output (['/usr/local/bin/TN93dist', path1, 'COUNT', str(0.01), 'RESOLVE', 'CSV', '100', '0', path2], ) 
        tn93result = tn93xtract.search (output.decode("utf-8"))
        return (int(tn93result.group(1)), int(tn93result.group(2)))
    except:
        pass
    return None

def main (cache_file, cache_file_pair):
    if os.path.exists(cache_file):
        with open (cache_file, "r") as fh:
            previous_run_cache = json.load (fh)
    else:
        previous_run_cache = {}
        
    if os.path.exists(cache_file_pair):
        with open (cache_file_pair, "r") as fh:
            previous_pair_cache = json.load (fh)
    else:
        previous_pair_cache = {}

    for file1, file2 in itertools.combinations (previous_run_cache.keys(), 2):
        pair_key = '|'.join ([file1,file2])
        if 'aiedrp_id' in previous_run_cache[file1] and 'aiedrp_id' in previous_run_cache[file2]:
            if previous_run_cache[file1]['aiedrp_id'] == previous_run_cache[file2]['aiedrp_id'] or previous_run_cache[file1]['aiedrp_id'] is None or previous_run_cache[file2]['aiedrp_id'] is None: 
                continue
            if pair_key not in previous_pair_cache:
                previous_pair_cache [pair_key] = None
                if 'tn93' in previous_run_cache[file1] and 'tn93' in previous_run_cache[file2] and previous_run_cache[file1]['tn93'] is not None and previous_run_cache[file2]['tn93'] is not None:
                    if  previous_run_cache[file1]['tn93'][1] > 0 and previous_run_cache[file1]['tn93'][1] > 0:
                        previous_pair_cache [pair_key] = get_tn93_pair (previous_run_cache[file1]['codon_alignment'], previous_run_cache[file2]['codon_alignment'],previous_run_cache[file1]['aiedrp_id'],previous_run_cache[file2]['aiedrp_id'])
                        print (previous_pair_cache [pair_key] )
                        with open (cache_file_pair, "w") as fh:
                                json.dump (previous_pair_cache, fh, sort_keys=True, indent=4)
                #return None
        
    with open (cache_file_pair, "w") as fh:
        json.dump (previous_pair_cache, fh, sort_keys=True, indent=4)

    return 0

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='scan the directory of 454 files and process them'
    )
    parser.add_argument(
        '-c', '--cache',
        metavar='JSON',
        type=str,
        help='the file which contains the .json cache for individual files',
        required = True
    )
    parser.add_argument(
        '-p', '--paircache',
        metavar='JSON_PAIR',
        type=str,
        help='the file which contains the .json cache for pairwise comparisons files',
        required = True
    )

    '''parser.add_argument(
        '-n', '--namecache',
        metavar='JSON_NAME',
        type=str,
        help='the file which contains the .json cache for names to ID mapping',
        required = True
    )'''

    args = None
    retcode = -1
    args = parser.parse_args()
        
    retcode = main(args.cache, args.paircache)
    
    sys.exit(retcode)


