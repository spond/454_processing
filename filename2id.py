import os, argparse, re, sys, xlrd3
import csv
import datetime, shutil, json
#import xlsx
from os.path import join, splitext, isfile


def minimalist_xldate_as_datetime(xldate, datemode):
     return (
        datetime.datetime(1899, 12, 30)
        + datetime.timedelta(days=xldate + 1462 * datemode)
        )


def main (dir, cache_file):
    fna = re.compile ("([0-9]+).+\.fna$")
    xls = re.compile ("\.xls$")
    mapper = re.compile ("\.mapper$")
    xlsx = re.compile ("^[^\.]+\.xlsx$")
    taginname = re.compile ("^([A-Z][0-9]+)\ ([0-9]+)")
    
    if os.path.exists(cache_file):
        with open (cache_file, "r") as fh:
            list_of_fna = json.load (fh)
    else:
        list_of_fna = {}
        
    for root, dirs, files in os.walk(dir):
        haz_xls = False
        haz_csv = True
        xls_map = {}
        csv_map = {}
        locallist = {}
        for file in files:
            ma = fna.search (file)
            if ma is not None:
                base_path = join(root, splitext(file)[0]);
                if base_path not in list_of_fna and isfile ( base_path + ".qual"):
                    pat = taginname.search (file)
                    if pat is not None:
                        locallist[base_path] = [pat.group(1), datetime.datetime.strptime(pat.group(2),"%m%d%Y")]
                        #print(locallist[base_path]) 
                    else:
                        locallist[base_path] = int(ma.group(1))
                    #print (base_path)
            else:
                if xls.search (file) is not None:
                    #print ("\n\n\nHAZ excel! %s %s" % (root,file) )
                    try:
                        workbook = xlrd3.open_workbook (join (root, file))
                        info = workbook.sheet_by_name('Sheet1')
                        header_row = info.row_values(0)
                   
                        mbn_id =  header_row.index('MBN')
                        sample_date = header_row.index('Sample Date')
                        sample_well = header_row.index('Sample Well')
                        
                        for rownum in range(1,info.nrows):
                             da_row = info.row_values(rownum)
                             xls_map [int (da_row[sample_well])] = [da_row[mbn_id], minimalist_xldate_as_datetime (da_row[sample_date], 1)]
                             
                    except:
                        pass
                        
                    haz_xls = True

                if mapper.search (file) is not None:
                    #print ("\n\n\nHAZ! %s %s" % (root,file) )
                    try:
                        data_reader = csv.reader(open(join (root, file), 'r'))
                        for row in data_reader:
                            if len (row) == 3:
                                 csv_map[int(row[0])] = [row[1],datetime.datetime.strptime(row[2],"%m/%d/%Y")]
                            else:
                                raise BaseException ("FAIL")
                        #print (csv_map)
                    except:
                        raise
                    haz_csv = True
                 
        done_by_map = False       
        for k,l in [(haz_xls, xls_map), (haz_csv, csv_map)]:        
            if k and len (l) == len (locallist):
                for fname, val in locallist.items():
                    locallist[fname] = l[val]
                list_of_fna.update (locallist)
                done_by_map = True
                break
        
        if not done_by_map:
            for f, v in locallist.items ():
                if isinstance (v, list):
                    list_of_fna [f] = v    
                else:
                	print ("Unknown sample %s" % f)
        
    
        
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None   
    with open (cache_file, "w") as fh:
        json.dump (list_of_fna, fh, default=dthandler, sort_keys=True, indent=4)

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
        
    retcode = main(args.input, args.cache)
    
    sys.exit(retcode)


