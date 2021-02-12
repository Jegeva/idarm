#! /usr/bin/env python3
# copyright : jean-georges valle 2020
import argparse
import inspect
import os
import sys
from datetime import datetime
import time
import csv

sys.path = [os.path.join(os.getcwd(),"cmsis-svd/python/")] + sys.path

import cmsis_svd
from cmsis_svd.parser import SVDParser
from idarm.persistance import persistance
from idarm.utils import utils
from idarm.frontend import frontend
from idarm.backend import backend
from idarm.data import data

config = {}


def rename_database(database):
    if os.path.isfile(database):
        os.rename(database,database +"." + str(os.path.getmtime(database))  + '.old')


def main():
    base_sz_default = "0x1000"
    
    parser = argparse.ArgumentParser(description='makes segments for ida given a svd descripted ARM chip')
    parser.add_argument('-v', '--vendor', type=str,default=None, help='chip vendor, (needs a model)')
    parser.add_argument('-c', '--chip',   type=str,default=None, help='chip model ,(needs a vendor)')
    parser.add_argument('-C', '--core',   type=str,default=None, help='a specific core')

    #default 1    Meg
    parser.add_argument('-m', '--max-segment-sz',   type=str    , help='max segment size (fallback to db, then 0x%08x) if you need that for some reason' % (int(base_sz_default,0)))
    parser.add_argument('--max-segment-sz-int',   type=int, help='chip model', default=0)
    parser.add_argument('-d', '--database', type=str, default='./db.sqlite3')
    parser.add_argument('-D', '--dump', default=False, action='store_true')
    parser.add_argument('-r', '--rebuild-database', default=False, action='store_true')
    parser.add_argument('-n', '--no-database', default=False, action='store_true')
    parser.add_argument('-N', '--no-descriptions', default=False, action='store_true')
    parser.add_argument('-V', '--verbose', default=False, action='store_true')
    args = parser.parse_args()
    
    args.cmsis_svd_datapath = os.path.abspath(os.path.join(inspect.getfile(cmsis_svd), os.pardir)) + os.path.sep +"data"
    args.core_svd_datapath = os.path.join(os.getcwd(),"ads2svd/out/")
   

    
    if(args.max_segment_sz):
        args.max_segment_sz_int = int(args.max_segment_sz,0)
    else:
        args.max_segment_sz_int = int(base_sz_default,0)
        
    config['vendors'] = os.listdir(args.cmsis_svd_datapath)
    if(args.vendor):
        if(not args.vendor in config['vendors']):
            utils.eprint("unknown vendor : %s" % (args.vendor))
            exit()

    print("P",args.cmsis_svd_datapath, args.core_svd_datapath)


    if(args.rebuild_database):
        rename_database(args.database)
        config["data"] = data(None,args.database,args.core_svd_datapath ,args.cmsis_svd_datapath, args.max_segment_sz_int,args.vendor,args.core,args.chip,args.no_descriptions)
    else :
        if(args.no_database):
            config["data"] = data("svd",args.database,args.core_svd_datapath ,args.cmsis_svd_datapath, args.max_segment_sz_int,args.vendor,args.core,args.chip,args.no_descriptions)
        else :
            config["data"] = data("db",args.database,args.core_svd_datapath ,args.cmsis_svd_datapath, args.max_segment_sz_int,args.vendor,args.core,args.chip,args.no_descriptions)
        
    config['args'] = args

    if(args.dump):
        print(config)
        config["data"].dump_data()

if __name__ == "__main__":
    main()
