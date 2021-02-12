# copyright : jean-georges valle 2020
import cmsis_svd
from cmsis_svd.parser import SVDParser
import cProfile
import os
import sys
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

    verbose = False

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


    def set_verbose(v):
        data.verbose = v

    def dump_data(self):
        if(data.verbose):
            pp = HexPrettyPrinter()
            pp.pprint(  self.data_top_hash)



    def parse_chip_svd(self,chip,parser):
       

        segments = {}
        peripherals = {}
       
        chip["cpu"] = parser.get_device().cpu.name
        if(chip["cpu"] != None):
            if(chip["cpu"].lower().find("cortex-") ==0):
                chip["cpu"] = chip["cpu"][7:]
            if(chip["cpu"].lower().find("cm") ==0):
                chip["cpu"] = chip["cpu"][1:]
            if(chip["cpu"][-1:] == "P"):
                chip["cpu"] = chip["cpu"][:-1] + "+"
            if(chip["cpu"][-4:] .lower()== "plus"):
                chip["cpu"] = chip["cpu"][:-4] + "+"

        if(data.verbose):
            print(chip["cpu"])

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
                    if(r.name[:len(peripheral.name)+1]) == (peripheral.name+"_"):
                        reg["name"] = r.name[len(peripheral.name)+1:]
                    else:
                        reg["name"] = r.name

                    reg["name"] = reg["name"].replace("[","_")
                    reg["name"] = reg["name"].replace("]","_")
                    if(r.size):
                        reg["size"] = int(r.size)
                    else:
                        reg["size"] = 32
                    reg["addr"] = peripheral.base_address + r.address_offset
                    reg["offset"] = r.address_offset
                    if(r.reset_value != None and r.reset_mask != None):
                        reg["initval"] = r.reset_value & r.reset_mask
                    else:
                        if(r.reset_value != None ):
                            reg["initval"] = r.reset_value
                        else:
                            reg["initval"] = 0
                    reg["fields"] = {}
                    peripherals[ peripheral.base_address  ]["registers"][ reg["addr"] ] = reg
                    if r.fields :
                        for b in r.fields:
                            reg["fields"][ b.name ] = {}
                            reg["fields"][ b.name ]["bito"] = int(b.bit_offset);
                            reg["fields"][ b.name ]["bitw"] = int(b.bit_width);
                            reg["fields"][ b.name ]["desc"] = b.description;
                            reg["fields"][ b.name ]["access"] = 3
                            reg["fields"][ b.name ]["enums"] = {}
                            if(b.access):
                                if(b.access=="read-only"):
                                    reg["fields"][ b.name ]["acces"] = 1
                                if(b.access=="write-only"):
                                    reg["fields"][ b.name ]["acces"] = 2
                            if(b.enumerated_values):
                                for e in b.enumerated_values:
                                    reg["fields"][ b.name ]["enums"][e.name] = {}
                                    reg["fields"][ b.name ]["enums"][e.name]["name"] = e.name;
                                    if(e.value):
                                        reg["fields"][ b.name ]["enums"][e.name]["value"] = int(e.value);
                                    else:
                                        reg["fields"][ b.name ]["enums"][e.name]["value"] = 0;
                                    reg["fields"][ b.name ]["enums"][e.name]["desc"] = e.description;





        chip["segments"]=self.compress_contiguous_segments(segments,self.segsz)
        chip["peripherals"]=peripherals

    def core_data_from_svd(self,core_svd_datapath,segment_size,core):
        if core == None:
            for f in sorted(glob.glob(os.path.join(core_svd_datapath,'*.svd'))):
                c=f.split(os.path.sep)[-1][:-4]
                if(c.lower().find("cortex-") ==0):
                    c = c[7:]
                if(c.lower().find("CM") ==0):
                    c = c[1:]
                print(f,"\t",c)
                self.data_top_hash["cores"][c]= {}
                self.data_top_hash["cores"][c]["file"]= f
                self.data_top_hash["cores"][c]["dirty"]= True
        else:
            f = os.path.join(core_svd_datapath,core) + ".svd"
            if(core.lower().find("cortex-") > -1):
                core = core[7:]

            self.data_top_hash["cores"][core]= {}
            self.data_top_hash["cores"][core]["file"]= f
            self.data_top_hash["cores"][core]["dirty"]= True

        for c in self.data_top_hash["cores"].keys():
            #print("---------->",core_svd_datapath ,c + '.svd')
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
    
    def __init__(self, data_from,db_path,core_svd_datapath,cmsis_svd_datapath,segment_size,vendor,core,chip,nodesc):
        self.data_top_hash = {}
        self.data_top_hash["vendors"] = {}
        self.data_top_hash["cores"] = {}
        self.persistance = persistance(db_path,cmsis_svd_datapath,segment_size)
        self.segsz = segment_size
        self.segment_mask = self.get_segsz_mask(self.segsz)
        #print("P",cmsis_svd_datapath, core_svd_datapath)
        if data_from == None :
            self.core_data_from_svd(core_svd_datapath,segment_size,core)
  #          self.dump_data()
            self.data_from_svd(cmsis_svd_datapath,segment_size,vendor,chip)               
            self.persistance.persist(self.data_top_hash,nodesc)
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
