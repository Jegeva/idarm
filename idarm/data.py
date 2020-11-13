import cmsis_svd
from cmsis_svd.parser import SVDParser

import os
import time
import glob
import pprint
from pprint import PrettyPrinter

from .utils import utils
from .persistance import persistance



class HexPrettyPrinter(PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        repr, readable, recursive = PrettyPrinter.format(self, object, context, maxlevels, level)
        if isinstance(object, int):
            return "0x{0:x}".format(object), readable, recursive
        else:
            return repr, readable, recursive



class data:
    
    def get_segsz_mask(self,sz):
        i=0
        while(sz):
            sz>>=1;
            i+=1
        # python and ~ sometimes...
        return ((0xffffffff>>i)<<i)

    def compress_contiguous_segments(self,segments,ssz):
        ret = {}
        kl = sorted(segments.keys())
        if(len(kl)<1):
            return ret
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

    def dump_data(self):
        pp = HexPrettyPrinter()
        pp.pprint(  self.data_top_hash)



    def parse_chip_svd(self,chip,parser):
       
        data= {}
        segments = {}
        peripherals = {}
       
        
        for peripheral in parser.get_device().peripherals:
            #print("0x%08x %s" %( peripheral.base_address,peripheral.name))
            regs = None
            if(peripheral.base_address):
                start_a = peripheral.base_address & self.segment_mask
                end_a = (peripheral.base_address & self.segment_mask) + self.segsz
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
                    reg["offset"] = r.address_offset
                    if(r.reset_value != None and r.reset_mask != None):
                        reg["initval"] = r.reset_value & r.reset_mask
                    else:
                        if(r.reset_value != None ):
                            reg["initval"] = r.reset_value
                        else:
                            reg["initval"] = 0
                    peripherals[ peripheral.base_address  ]["registers"][ reg["addr"] ] = reg
        chip["segments"]=self.compress_contiguous_segments(segments,self.segsz)
        chip["peripherals"]=peripherals

    def core_data_from_svd(self,core_svd_datapath,segment_size,core):
        if core == None:
            for f in sorted(glob.glob(os.path.join(core_svd_datapath,'*.svd'))):
                c=f.split(os.path.sep)[-1][:-4]
                print(f,"\t",c)
                self.data_top_hash["cores"][c]= {}
                self.data_top_hash["cores"][c]["file"]= f
                self.data_top_hash["cores"][c]["dirty"]= True
        else:
            f = os.path.join(core_svd_datapath,core) + ".svd"
            self.data_top_hash["cores"][core]= {}
            self.data_top_hash["cores"][core]["file"]= f
            self.data_top_hash["cores"][core]["dirty"]= True

        for c in self.data_top_hash["cores"].keys():
            print("---------->",core_svd_datapath ,c + '.svd')
            self.parse_chip_svd(self.data_top_hash["cores"][c],SVDParser.for_xml_file( self.data_top_hash["cores"][c]["file"]))


    def data_from_svd(self,cmsis_svd_datapath,segment_size,vendor,chip):
        if vendor == None:
            self.vendors = os.listdir(cmsis_svd_datapath)
            for v in self.vendors:
                self.data_top_hash["vendors"][v]= {}
                for f in glob.glob(os.path.join(cmsis_svd_datapath,v,'*.svd')):
                    c=f.split(os.path.sep)[-1][:-4]
                    self.data_top_hash["vendors"][v][c]= {}
                    self.data_top_hash["vendors"][v][c]["file"]= f
                    self.data_top_hash["vendors"][v][c]["dirty"]= True
        else:
            self.vendors = [vendor]
            self.data_top_hash["vendors"][vendor] = {}
            if(chip):
                self.data_top_hash["vendors"][vendor][chip]= {}
                self.data_top_hash["vendors"][vendor][chip]["file"]= os.path.join(cmsis_svd_datapath,vendor,chip + '.svd')
                self.data_top_hash["vendors"][vendor][chip]["dirty"]= True
            else:
                for f in glob.glob(os.path.join(cmsis_svd_datapath,vendor,'*.svd')):
                    c=f.split(os.path.sep)[-1][:-4]
                    self.data_top_hash["vendors"][vendor][c]= {}
                    self.data_top_hash["vendors"][vendor][c]["file"]= f
                    self.data_top_hash["vendors"][vendor][c]["dirty"]= True

            #print(   self.data_top_hash)
        for v in self.data_top_hash["vendors"].keys():
            for c in sorted(self.data_top_hash["vendors"][v].keys()):
                print(v,c)
                self.parse_chip_svd(self.data_top_hash["vendors"][v][c],SVDParser.for_packaged_svd(v, c + '.svd'))
    
    def __init__(self, data_from,db_path,core_svd_datapath,cmsis_svd_datapath,segment_size,vendor,core,chip):
        self.data_top_hash = {}
        self.data_top_hash["vendors"] = {}
        self.data_top_hash["cores"] = {}
        self.persistance = persistance(db_path,cmsis_svd_datapath,segment_size)
        self.segsz = segment_size
        self.segment_mask = self.get_segsz_mask(self.segsz)
        print("P",cmsis_svd_datapath, core_svd_datapath)
        if data_from == None :
            self.core_data_from_svd(core_svd_datapath,segment_size,core)
            self.data_from_svd(cmsis_svd_datapath,segment_size,vendor,chip)               
            self.persistance.persist(self.data_top_hash)
        else:
            if(data_from == "db"):
                if(vendor == None):
                    self.persistance.restore_all(self.data_top_hash)
                else:
                    if(chip == None):
                        self.persistance.restore_vendor(self.data_top_hash,vendor)
                    else:
                        self.persistance.restore_chip(self.data_top_hash,vendor,chip)
            else:
                self.data_from_svd(cmsis_svd_datapath,segment_size,vendor,chip)       
                        

            
        self.dump_data()
