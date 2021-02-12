#! /usr/bin/python3
import os
import glob
import cmsis_svd
import pprint
from cmsis_svd.parser import SVDParser

import pprint
class data:
    
    def parse_core(self,filepath,parser):
        d = parser.get_device()
        k = d.cpu
        dn = d.name
        
   

        core = {}

        if( dn not in self.cores):
            self.cores[dn] = {}
               
        core["file"] = filepath

       
        
        core["peripherals"] = {}        
        for p in d.peripherals:
            pn = p.name
            if pn not in core["peripherals"].keys():
                core["peripherals"][pn] = {}
                core["peripherals"][pn]["registers"] = {}
                
            core["peripherals"][pn]["address"] = p.base_address
            #print(pn, p.base_address)
            
            rn = None
            for r in p.registers:
                rn = r.name.upper()
                if rn not in core["peripherals"][pn]["registers"].keys():
                    core["peripherals"][pn]["registers"][rn] = {}
                    core["peripherals"][pn]["registers"][rn]["fields"] = {}
                    core["peripherals"][pn]["registers"][rn]["name"] = rn
                    core["peripherals"][pn]["registers"][rn]["size"] = r.size
                    core["peripherals"][pn]["registers"][rn]["access"] = r.access
                for f in r.fields:
                    fn = f.name
                                   
                    if fn not in core["peripherals"][pn]["registers"][rn]["fields"].keys():
                        core["peripherals"][pn]["registers"][rn]["fields"][fn] = {}
                        core["peripherals"][pn]["registers"][rn]["fields"][fn]["enums"] = {}
                    core["peripherals"][pn]["registers"][rn]["fields"][fn]["name"] = fn
                    core["peripherals"][pn]["registers"][rn]["fields"][fn]["description"] = f.description
                    core["peripherals"][pn]["registers"][rn]["fields"][fn]["offset"] = f.bit_offset
                    core["peripherals"][pn]["registers"][rn]["fields"][fn]["width"] = f.bit_width
                    if(f.enumerated_values):
                        for e in f.enumerated_values :
                            en = e.name
                            core["peripherals"][pn]["registers"][rn]["fields"][fn]["enums"][en] = e.value

        sr=None
        if 'CPSR' in core["peripherals"]["Core"]["registers"]:
            sr = core["peripherals"]["Core"]["registers"]["CPSR"]
        if 'XPSR' in core["peripherals"]["Core"]["registers"]:
            sr = core["peripherals"]["Core"]["registers"]["XPSR"]

        #print(sr)
        arch = "AArch32"
        arch64cnt=0
        core["version"] = "7"
        if "M" in sr["fields"]:
            if len([a  for a in sr["fields"]["M"]["enums"].keys() if(a[:7] == "AArch32")]) > 0:
                core["version"] = "8"
            if len([a  for a in sr["fields"]["M"]["enums"].keys() if(a[:7] == "AArch64")]) > 0:
                arch64cnt=1

            if( core["version"] == "8" and  arch64cnt==0):
                core["version"] = "8R"

        if( dn in self.cores):
            if "AArch32" in self.cores[dn]:
                 arch = "AArch64"
                 core["version"] = self.cores[dn]["AArch32"]["version"]
                
                
        if dn not in self.cores:
            self.cores[dn]={}
        self.cores[dn][arch] = core

        print( filepath, k.name,core["version"],arch )
        

        
                

    def parse_cores(self,core_svd_datapath):
        self.core_files = sorted(glob.glob(os.path.join(core_svd_datapath,'*.svd')))
        self.cores = {}
        pp = pprint.PrettyPrinter(indent=4)
        for c in self.core_files:      
            self.parse_core(c,SVDParser.for_xml_file(c))
            
            
        #pp.pprint(self.cores)
        

    def __init__(self, core_svd_datapath):
        self.data_top_hash = {}
        self.cores = {}    
        self.parse_cores(core_svd_datapath)
        
        #print( self.cores)

def main():
    d= data("ads2svd/out/")
    
if __name__ == "__main__":
    main()

