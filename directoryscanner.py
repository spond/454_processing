import os, argparse, re, sys, xlrd3
import subprocess, time, csv
import datetime, shutil, json
#import xlsx
from os.path import join, splitext, isfile

tn93xtract = re.compile ('Found ([0-9]+) links among ([0-9]+) pairwise comparisons')

def minimalist_xldate_as_datetime(xldate, datemode):
     return (
        datetime.datetime(1899, 12, 30)
        + datetime.timedelta(days=xldate + 1462 * datemode)
        )

def filter_454 (base_path, results_path):
    print ("Running filter454 on %s " % base_path)
    out_file = open (results_path, "w")
    try:
        subprocess.check_call (['/usr/local/bin/454filter', base_path + '.fna', base_path + '.qual', '10', '50', '7'], stdout = out_file) 
    except:
        return None
    return results_path

def codon_aligner (in_path, out_path):
    print ("Running codonaligner on %s " % in_path)
    try:
        subprocess.check_call (['/usr/bin/bpsh', '3', '/usr/local/bin/codonaligner', '-r', 'HXB2_rt', '-o', out_path, in_path]) 
    except:
        return None
    return out_path

def get_tn93_self (in_path):
    print ("get_tn93_self on %s" % in_path)
    try:
        output = subprocess.check_output (['/usr/bin/bpsh', '7', '/usr/local/bin/TN93dist', in_path, 'COUNT', str(0.01), 'RESOLVE', 'CSV'], ) 
        #output = subprocess.check_output (['/usr/local/bin/TN93dist', in_path, 'COUNT', str(0.01), 'RESOLVE', 'CSV'], ) 
        tn93result = tn93xtract.search (output.decode("utf-8"))
        return (int(tn93result.group(1)), int(tn93result.group(2)))
    except:
        return None
        
def assign_name (in_id, mapping_dic):  
    if in_id in mapping_dic[2]:
        return (mapping_dic[1][mapping_dic[2].index(in_id)],mapping_dic[3][mapping_dic[2].index(in_id)])
    elif in_id.lower() in mapping_dic[0]:
        idof = mapping_dic[0].index(in_id.lower())
        name = mapping_dic[1][idof]
        if (len (name)):  
            return (name, mapping_dic[3][idof])
        else:
            return (in_id, mapping_dic[3][idof])
    return (None,None)

def main (dir, cache_file, name_cahe, results_dir, mapper_file):
    list_of_fna = {} # file : directory; assumes that both file.fna and file.qual exist
    fna = re.compile ("([0-9]+).+\.fna$")
    xls = re.compile ("^[^\.]+\.xls$")
    xlsx = re.compile ("^[^\.]+\.xlsx$")
    '''
    mapper = csv.reader (open (mapping_file, "r"))
    mapperList = [[], [], []]
    
    next(mapper)
    for r in mapper:
        for index,c in enumerate(r):
            mapperList[index].append (c)
    '''
    with open (name_cahe, "r") as fh:
        names_cache = json.load (fh)
            
    if os.path.exists(cache_file):
        with open (cache_file, "r") as fh:
            previous_run_cache = json.load (fh)
    else:
        previous_run_cache = {}
        
    mapper_reader = csv.reader (open (mapper_file, "r"))
    next (mapper_reader)
    mapping_dic = [[],[],[],[]]
    for r in mapper_reader:
        for index,c in enumerate (r):
            mapping_dic[index].append(c)
        
    for root, dirs, files in os.walk(dir):
        haz_xls = False
        xls_map = {}
        locallist = {}
        for file in files:
            ma = fna.search (file)
            if ma is not None:
                base_path = join(root, splitext(file)[0]);
                if isfile ( base_path + ".qual"):
                    locallist[base_path + ".fna"] = int(ma.group(1))
                    if base_path not in names_cache: 
                        continue

                    if base_path not in previous_run_cache:
                        previous_run_cache [base_path] = {'id' : len (previous_run_cache) + 1}
                        
                    previous_run_cache [base_path]['patient_id'] = names_cache [base_path][0]
                    previous_run_cache [base_path]['sample_date'] = time.strptime(names_cache [base_path][1],"%Y-%m-%dT%H:%M:%S")
                    
                    #print (previous_run_cache [base_path]['sample_date'])
                    
                    (previous_run_cache [base_path]['aiedrp_id'],previous_run_cache [base_path]['mi']) = assign_name (previous_run_cache [base_path]['patient_id'], mapping_dic)
                    
                    if previous_run_cache [base_path]['sample_date'].tm_year < 1990:
                        continue
                    else:
                    	print ('Working on %s -> %s:%s:%s' % (base_path,previous_run_cache [base_path]['patient_id'], str ( previous_run_cache [base_path]['sample_date']),str ( previous_run_cache [base_path]['aiedrp_id'])))
                    	
                        
                    if 'filtered_alignment' not in previous_run_cache [base_path]:
                        previous_run_cache [base_path] ['filtered_alignment'] = filter_454 (base_path, join (results_dir, str(previous_run_cache [base_path]['id']) + "_raw.fas"))
                    if previous_run_cache [base_path] ['filtered_alignment'] is not None:
                        if 'codon_alignment' not in previous_run_cache [base_path] or previous_run_cache [base_path]['codon_alignment'] is None:
                            previous_run_cache [base_path] ['codon_alignment'] = codon_aligner (join (results_dir, str(previous_run_cache [base_path]['id']) + "_raw.fas"), join (results_dir, str(previous_run_cache [base_path]['id']) + ".fas"))
                    if 'codon_alignment' in previous_run_cache [base_path] and previous_run_cache [base_path] ['codon_alignment'] is not None:
                        if 'tn93' not in previous_run_cache [base_path] or previous_run_cache [base_path]['tn93'] == None:
                            previous_run_cache [base_path] ['tn93'] = get_tn93_self (previous_run_cache [base_path] ['codon_alignment'])
        
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None  
    with open (cache_file, "w") as fh:
        json.dump (previous_run_cache, fh,default=dthandler, sort_keys=True, indent=4)
    return 0

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='scan the directory of 454 files and process them'
    )
    parser.add_argument(
        '-i', '--input',
        metavar='DIR',
        type=str,
        help='the directory to scan',
        required = True,
    )
    parser.add_argument(
        '-c', '--cache',
        metavar='JSON',
        type=str,
        help='the file which contains the .json cache file',
        required = True,
    )
    parser.add_argument(
        '-r', '--results',
        metavar='RESULTS',
        type=str,
        help='the directory where analysis results will be written',
        required = True,
    )
    parser.add_argument(
        '-n', '--names',
        metavar='names',
        type=str,
        help='the JSON file with name resolutions',
        required = True,
    )
    parser.add_argument(
        '-m', '--mapper',
        metavar='mapper',
        type=str,
        help='the CSV annotation mapepr',
        required = True,
    )
    
    
    
    args = None
    retcode = -1
    args = parser.parse_args()
    
    if not os.path.exists (args.results):
        os.mkdir (args.results) 
    
    retcode = main(args.input, args.cache, args.names, args.results,args.mapper)
    
    sys.exit(retcode)


