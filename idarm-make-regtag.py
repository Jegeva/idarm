#! /usr/bin/python2

from __future__ import print_function


import sqlite3
import argparse
import inspect
import os
import sys
import struct
from datetime import datetime
import time

sys.path = ["./cmsis-svd/python/"] + sys.path

import cmsis_svd
from cmsis_svd.parser import SVDParser



def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_ven_chip_hash(datapath):
    ret = {}
    for v in sorted(os.listdir(cmsis_svd_datapath)):
        if(v[0] != '.'):
            ret[v]={}
            for c in sorted(os.listdir(cmsis_svd_datapath + os.path.sep +v )):
                if(c[-3:]=="svd"):
                    d = c[:-4]
                    ret[v][d] = 1
    return ret

def get_segsz_mask(sz):
    i=0
    while(sz):
        sz>>=1;
        i+=1
        # python and ~ sometimes...
    return ((0xffffffff>>i)<<i)

def compress_contiguous_segments(segments,ssz):
    ret = {}
    kl = sorted(segments.keys())
    i = 0;    
    lastel= [segments[kl[i]][0] , segments[kl[i]][1]]

    while(i< len(kl)):
        if( (lastel[1] == segments[kl[i]][0])  or   ((lastel[1]+ssz) == segments[kl[i]][0])  ):
            lastel[1] = segments[kl[i]][1]
        else:
            ret[str(lastel[0]) + '-' + str(lastel[1])] = lastel    
            lastel= [segments[kl[i]][0] , segments[kl[i]][1]]    
        i+=1
    ret[str(lastel[0]) + '-' + str(lastel[1])] = lastel
    return ret

def get_data_for(vendor,chip,segsz,args,db):
    data= {}
    segments = {}
    peripherals = {}    
    if os.path.isfile(args.database) and db:
        conn = sqlite3.connect(args.database)
        cur = conn.cursor()
        cur.execute("SELECT segsz FROM db_info")
        rows = cur.fetchall()           
        if(rows[0][0] == args.max_segment_sz_int):
            cur = conn.cursor()
            cur.execute("SELECT segsz FROM db_info")
            rows = cur.fetchall()
            if rows[0][0] == args.max_segment_sz_int :
                cur.execute("SELECT chips.id from chips,vendors where chip='%s' and vendor='%s'" % (chip,vendor))            
                rows = cur.fetchall()
                cid = rows[0][0]
                #print(cid)
                cur.execute("SELECT addr_start,addr_end from chip_segments,segments where cid=%d and sid=segments.id" % (cid))
                rows = cur.fetchall()
                #print(rows)
                for r in rows:
                    #print(r)
                    segments[ str(r[0]) + "-" + str(r[0])]= [r[0],r[1]]      
    if(len(segments) == 0):
        #can't get from db or db disabled : parse
        segment_mask = get_segsz_mask(segsz)
        print(vendor, chip)
        parser = SVDParser.for_packaged_svd(vendor, chip + '.svd')
        for peripheral in parser.get_device().peripherals:
            #print("0x%08x %s" %( peripheral.base_address,peripheral.name))
            start_a = peripheral.base_address & segment_mask
            end_a = (peripheral.base_address & segment_mask)+2*segsz
            segments[ str(start_a) + "-" +str(end_a)  ] = [ start_a,end_a]
            
            peripherals[ peripheral.base_address  ] = {}
            peripherals[ peripheral.base_address  ]["name"] = peripheral.name
            peripherals[ peripheral.base_address  ]["registers"] = {}
            regs  = peripheral.registers
            #print(peripheral.name,peripheral.base_address,flush=True)
            #print(regs)
            if(regs):
                for r in  regs:
                    reg = {}
                    reg["name"] = r.name
                    reg["addr"] = peripheral.base_address + r.address_offset
                    if(r.reset_value != None and r.reset_mask != None):
                        reg["initval"] = r.reset_value & r.reset_mask
                    else:
                        if(r.reset_value != None ):
                            reg["initval"] = r.reset_value
                        else:
                            reg["initval"] = None
                 
    #return segments
    data["segments"] = compress_contiguous_segments(segments,segsz)
    return data

def build_db(cmsis_svd_datapath,args):
    
    toph = get_ven_chip_hash(cmsis_svd_datapath)
    if not os.path.isfile(args.database):
        eprint("building db\n")
        vendorid = 0;
        chipid = 0
        conn = sqlite3.connect(args.database)
        segments = {}
        segmentid=0;
        sqlf = open('bd.sql')
        sql= sqlf.read().split(';');
        sqlf.close()        
        for l in sql:
            #print(l)
            conn.execute(l);
        conn.execute("insert into db_info values(%d,%d)" % ( time.time(), args.max_segment_sz_int ))            
        for v in sorted(toph):
            sql = "insert into vendors values(%d,'%s');" % (vendorid,v)
            conn.execute(sql);
            conn.commit()
            for c in sorted(toph[v]):
                chipstr = "%s %s %d %d                                     " % (v,c,chipid,vendorid)
                print(chipstr, end= "\r")
                toph[v][c] = {}
                toph[v][c]["data"] = get_data_for(v,c,args.max_segment_sz_int,args,0)
                toph[v][c]["segments"] = toph[v][c]["data"]["segments"]
                sql = "insert into chips values(%d,'%s', %d);" % (chipid,c,vendorid)
                conn.execute(sql);
                conn.commit()
                for s in toph[v][c]["segments"].keys():
                    if s not in segments:
                        sql = "insert into segments values(%d,%d,%d)" % (segmentid,toph[v][c]["segments"][s][0],toph[v][c]["segments"][s][1])
                        conn.execute(sql)
                        conn.commit()                            
                        segments[s] = segmentid
                        segmentid+=1
                    sql = "insert into chip_segments values(%d,%d)" % (segments[s],chipid)
                    conn.execute(sql);
                    conn.commit()                                                        
                chipid+=1
            vendorid+=1
        conn.commit()         
        conn.close()
    else:
        eprint("existing db\n")
    return sqlite3.connect(args.database)

            
if __name__ == "__main__":

    base_sz_default = "0x10000"
    
    parser = argparse.ArgumentParser(description='makes segments for ida given a svd descripted ARM chip')
    parser.add_argument('-v', '--vendor', type=str, help='chip vendor, (needs a model)')
    parser.add_argument('-c', '--chip',   type=str, help='chip model ,(needs a vendor)')
    #default 1 Meg
    parser.add_argument('-m', '--max-segment-sz',   type=str    , help='max segment size (fallback to db, then 0x%08x)' % (int(base_sz_default,0)))
    #if u specify both, the str wins
    parser.add_argument('--max-segment-sz-int',   type=int, help='chip model', default=0)

    parser.add_argument('-d', '--database', type=str, default='./db.sqlite3')

    parser.add_argument('-r', '--rebuild-database', default=False, action='store_true')
    parser.add_argument('-n', '--no-database', default=False, action='store_true')

    
    args = parser.parse_args()
    cmsis_svd_datapath = os.path.abspath(os.path.join(inspect.getfile(cmsis_svd), os.pardir)) + os.path.sep +"data"
    vendors = os.listdir(cmsis_svd_datapath)

    if(args.no_database):
        args.database=''
    #print(args)
    
    dbdefsz=None
    if(not (args.rebuild_database or args.no_database )):
        if os.path.isfile(args.database) :
            conn = sqlite3.connect(args.database)
            cur = conn.cursor()
            cur.execute("SELECT segsz FROM db_info")
            rows = cur.fetchall()
            dbdefsz= "0x%08x" % (rows[0][0])

        


    if(args.max_segment_sz):
        args.max_segment_sz_int = int(args.max_segment_sz,0)
    else:
        if(dbdefsz):
            args.max_segment_sz_int = int(dbdefsz,0)
            args.max_segment_sz = dbdefsz
            print("segment size = %s (db)" % (dbdefsz) )
        else:
            args.max_segment_sz_int = int(base_sz_default,0)
            args.max_segment_sz = base_sz_default
            print("segment size = %s (fallback)" % (base_sz_default) )

  




    
    #print(cmsis_svd_datapath)
    if (args.vendor !=  None):

        
        if(args.vendor not in vendors):
            print("--vendor : unknown vendor",file=sys.stderr)
            eprint(vendors)
            exit()

        chips_svds = os.listdir(cmsis_svd_datapath + os.path.sep + args.vendor)
        chips      = [os.path.splitext(f)[0] for f in chips_svds]

        if(args.chip not in chips):
            print("--chip : unknown chip",file=sys.stderr)
            eprint(chips)
            exit()
            

        data = get_data_for(args.vendor, args.chip ,args.max_segment_sz_int,args,1)
        segments = data["segments"]
        for k in segments.keys():
            print("0x%08x 0x%08x" % (segments[k][0], segments[k][1]))

    if(args.rebuild_database):
        if os.path.isfile(args.database):
            conn = sqlite3.connect(args.database)
            cur = conn.cursor()
            cur.execute("SELECT generated,segsz FROM db_info")
            rows = cur.fetchall()           
            os.rename(args.database,args.database +"." + str(rows[0][0]) + "-" + str(rows[0][1])  + '.old')
            conn.close()
        build_db(cmsis_svd_datapath,args)
            
    if len(sys.argv)<=1:
        try:
            import idc
            import idautils
        except ImportError:
            print("no args and outside of ida, bye")
            exit()
            
            
            

   

