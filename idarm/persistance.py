# copyright : jean-georges valle 2020
from .utils import utils
import os
import sqlite3
import time
import csv

class persistance:

    def build_db_skel(self):
        sqlf = open('bd.sql')
        sql = sqlf.read().split(';');
        sqlf.close()
        sql = map(str.strip,sql)
        for l in sql:            
            try:
                self.conn.execute(l);
            except sqlite3.OperationalError:
                utils.eprint("ERR>",l)
        self.conn.execute("insert into db_info values(%d,%d)" % ( time.time(), self.segment_size ))
        self.conn.commit()

    def restore_chip_from_id(self,h,chipid,c,ctype):
        cur = self.conn.cursor()
        h[c] = {}
        h[c]["peripherals"] = {}
        h[c]["db_id"] = chipid
        h[c]["segments"] = {}
        h[c]["dirty"] = False
        cur.execute("SELECT addr_start,addr_end FROM segments, chip_segments where segments.id=chip_segments.sid and chip_segments.cid=%d" % (chipid))
        rows_s = cur.fetchall()
        for row_s in rows_s:
            k = "%d-%d" % (row_s[0],row_s[1])
            h[c]["segments"][k] = [row_s[0],row_s[1]]
        if(ctype==1):
            cur.execute("SELECT name FROM core_chips,cores where cores.id=core_chips.coid and core_chips.chid=%d" % (chipid))
            rows_c = cur.fetchall()
            for row_c in rows_c:
                  h[c]["cpu"] =row_c[0]

            cur.execute("SELECT pid,name,base_address FROM peripherals, chip_peripherals where peripherals.id=chip_peripherals.pid and chip_peripherals.cid=%d" % (chipid))
        else:
            cur.execute("SELECT pid,name,base_address FROM peripherals, core_peripherals where peripherals.id=core_peripherals.pid and core_peripherals.cid=%d" % (chipid))
        rows_p = cur.fetchall()
        for row_p in rows_p:
            periphid = row_p[0]
            baddr    = row_p[2]
            h[c]["peripherals"][baddr] = {}
            h[c]["peripherals"][baddr]["name"] = row_p[1]
            h[c]["peripherals"][baddr]["db_id"] = periphid
            h[c]["peripherals"][baddr]["registers"] = {}
            cur.execute("SELECT rid,name,offset,address,initval,sz FROM registers, peripheral_registers where registers.id=peripheral_registers.rid and peripheral_registers.pid=%d" % (periphid))
            rows_r = cur.fetchall()
            for row_r in rows_r:
                raddr = row_r[3]
                registerid=row_r[0]
                h[c]["peripherals"][baddr]["registers"][raddr] = {}
                h[c]["peripherals"][baddr]["registers"][raddr]["db_id"] = row_r[0]
                h[c]["peripherals"][baddr]["registers"][raddr]["name"]  = row_r[1]
                h[c]["peripherals"][baddr]["registers"][raddr]["offset"]= row_r[2]
                h[c]["peripherals"][baddr]["registers"][raddr]["address"]= raddr
                h[c]["peripherals"][baddr]["registers"][raddr]["initval"]= row_r[4]
                h[c]["peripherals"][baddr]["registers"][raddr]["sz"]= row_r[5]
                h[c]["peripherals"][baddr]["registers"][raddr]["fields"]= {}
                cur.execute("SELECT fid,name,bitw,offset,access,description FROM register_fields,fields where register_fields.rid=%d and register_fields.fid=fields.id" % (registerid))
                rows_f = cur.fetchall()
                for row_f in rows_f:
                    fieldid=row_r[0]
                    fname=row_r[1]
                    h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]= {}
                    h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]["db_id"]=row_r[0]
                    h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]["name"] =row_r[1]
                    h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]["bito"]= row_r[3]
                    h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]["bitw"]= row_r[2]
                    h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]["desc"]= row_r[5]
                    h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]["access"]=row_r[4]
                    h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]["enums"]={}
                    cur.execute("SELECT eid,name,description,value FROM fields_field_enumerateds,field_enumerated where fields_field_enumerateds.fid=%d and fields_field_enumerateds.eid=field_enumerated.id" % (fieldid))
                    rows_e = cur.fetchall()
                    for row_e in rows_e:
                        enumid=row_r[0]
                        ename=row_r[1]
                        h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]["enums"][ename]={}
                        h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]["enums"][ename]["db_id"] =row_r[0]
                        h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]["enums"][ename]["name"]  =row_r[1]
                        h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]["enums"][ename]["value"] =row_r[3]
                        h[c]["peripherals"][baddr]["registers"][raddr]["fields"][fname]["enums"][ename]["desc"]  =row_r[2]




    def restore_core(self,th,core):
        cur = self.conn.cursor()
        if("cores" not in th):
            th["cores"] = {}
        cur.execute("SELECT id,name FROM cores where name='%s'" % (core))
        rows_c = cur.fetchall()
        for row_c in rows_c:
            chipid = row_c[0]
            c = row_c[1]
            self.restore_chip_from_id( th["cores"] ,chipid,c,0)

    def restore_chip(self,th,v,chip):
        cur = self.conn.cursor()
        if ( v not in th):
            th["vendors"][v] = {}
        cur.execute("SELECT id,chip FROM chips where chip='%s'" % (chip))
        rows_c = cur.fetchall()
        for row_c in rows_c:
            chipid = row_c[0]
            c = row_c[1]
            self.restore_chip_from_id( th["vendors"][v],chipid,c,1)




    def restore_vendor(self,th,v):
        cur = self.conn.cursor()
        if ( v not in th):
            th["vendors"][v] = {}
        cur.execute("SELECT id FROM vendors where vendor='%s'" % (v))
        rows_v = cur.fetchall()
        for row_v in rows_v:
            vendid = row_v[0]
            cur.execute("SELECT chip FROM chips where vendorid=%d" % (vendid))
            rows_c = cur.fetchall()
            for row_c in rows_c:
                chip = row_c[0]
                self.restore_chip(th,v,chip)

    def restore_all(self,th):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM cores")
        rows_c = cur.fetchall()
        for row_c in rows_c:
            core = row_c[0]
            self.restore_core(th,core)

        cur.execute("SELECT vendor FROM vendors")
        rows_v = cur.fetchall()
        for row_v in rows_v:
            vendor = row_v[0]
            self.restore_vendor(th,vendor)

    def persist(self,th,nodesc):
        vendid = 0
        chipid = 0
        coreid = 0
        perid  = 0
        regid  = 0
        fieldid  = 0
        enumfid  = 0
        segid = 0
        chip_by_name_missing_core = {}
        cur = self.conn.cursor()

        for c in th["cores"].keys():
            cur.execute("SELECT id FROM cores where name='%s'" % (c))
            rows = cur.fetchall()
            if(len(rows)):
                coreid = rows[0][0]
            else:
                cur.execute("insert into cores values(%d,'%s')" % (coreid,c))
                self.conn.commit()
                for s in th["cores"][c]["segments"].keys():
                    cur.execute("insert into segments values(%d,%d,%d)" % (
                        segid,
                        th["cores"][c]["segments"][s][0],
                        th["cores"][c]["segments"][s][1]))
                    cur.execute("insert into core_segments values(%d,%d)" % ( segid,coreid))
                    segid+=1
                for p in th["cores"][c]["peripherals"].keys():
                       cur.execute("insert into peripherals values('%s',%d,%d)" % (
                          th["cores"][c]["peripherals"][p]["name"],
                           perid,
                           p))
                       cur.execute("insert into core_peripherals values(%d,%d)" % (coreid,perid))
                       th["cores"][c]["peripherals"][p]["dbid"] = perid
                       for r in  th["cores"][c]["peripherals"][p]["registers"]:
                           cur.execute("insert into registers values('%s',%d,%d,%d,%d,%d)" %
                                        (
                                            th["cores"][c]["peripherals"][p]["registers"][r]["name"],
                                            regid,
                                            th["cores"][c]["peripherals"][p]["registers"][r]["offset"],
                                            r,
                                            th["cores"][c]["peripherals"][p]["registers"][r]["initval"],
                                            th["cores"][c]["peripherals"][p]["registers"][r]["size"]
                                        )
                            )
                           cur.execute("insert into peripheral_registers values(%d,%d)" % (perid,regid))
                           th["cores"][c]["peripherals"][p]["dbid"] = coreid
                           for b in th["cores"][c]["peripherals"][p]["registers"][r]["fields"].keys():
                               if( th["cores"][c]["peripherals"][p]["registers"][r]["fields"][b]["desc"] == None or nodesc):
                                   th["cores"][c]["peripherals"][p]["registers"][r]["fields"][b]["desc"]=""
                               cur.execute("insert into fields values('%s',%d,%d,%d,%d,'%s')" % (
                                   b,
                                   fieldid,
                                   th["cores"][c]["peripherals"][p]["registers"][r]["fields"][b]["bitw"],
                                   th["cores"][c]["peripherals"][p]["registers"][r]["fields"][b]["bito"],
                                   th["cores"][c]["peripherals"][p]["registers"][r]["fields"][b]["access"],
                                   th["cores"][c]["peripherals"][p]["registers"][r]["fields"][b]["desc"].replace("'","")
                               ))
                               cur.execute("insert into register_fields values(%d,%d)" % (regid,fieldid))
                               for e in th["cores"][c]["peripherals"][p]["registers"][r]["fields"][b]["enums"]:
                                   if( th["cores"][c]["peripherals"][p]["registers"][r]["fields"][b]["enums"][e]["desc"] == None or nodesc):
                                        th["cores"][c]["peripherals"][p]["registers"][r]["fields"][b]["enums"][e]["desc"]=""
                                   cur.execute("insert into field_enumerated values('%s','%s',%d,%d)" % (
                                    e,
                                    th["cores"][c]["peripherals"][p]["registers"][r]["fields"][b]["enums"][e]["desc"].replace("'",""),
                                    enumfid,
                                    th["cores"][c]["peripherals"][p]["registers"][r]["fields"][b]["enums"][e]["value"]
                                   ))
                                   cur.execute("insert into fields_field_enumerateds values(%d,%d)" % (fieldid,enumfid))
                                   enumfid+=1
                               fieldid+=1
                           regid+=1
                       perid += 1
                th["cores"][c]["dbid"] = coreid
            coreid += 1


        for v in th["vendors"].keys():
            cur.execute("SELECT id FROM vendors where vendor='%s'" % (v))            
            rows = cur.fetchall()
            if(len(rows)):                
                vendid = rows[0][0]
            else:
                cur.execute("insert into vendors values(%d,'%s')" % (vendid,v))
                self.conn.commit()
            for c in th["vendors"][v].keys():
                if(th["vendors"][v][c]["dirty"]):
                    cur.execute("SELECT id FROM chips where vendorid=%d and chip='%s'" % (vendid,c))
                    rows = cur.fetchall()
                    if(len(rows)):
                        # chip exists drop it
                        chipid=rows[0][0]
                        cur.execute("delete from registers where id in (select rid from  peripheral_registers,chip_peripherals where chip_peripherals.cid=%d and chip_peripherals.pid= peripheral_registers.pid)" % (chipid))
                        cur.execute("delete from peripherals where id in (select pid from  chip_peripherals where chip_peripherals.cid=%d)" % (chipid))
                        cur.execute("delete from chips where id =%d" % (chipid))

                    if(th["vendors"][v][c]["cpu"] != None):
                        print("inserting",c,th["vendors"][v][c]["cpu"])
                        cur.execute("insert into core_chips values(%d,%d)" % (th["cores"][ th["vendors"][v][c]["cpu"]  ]["dbid"],chipid))
                    else:
                        print("missing core ",c)
                        if(c in chip_by_name_missing_core ):
                            chip_by_name_missing_core[c].append(chipid)
                        else:
                            chip_by_name_missing_core[c]=[chipid]


                    #print("insert into chips values(%d,'%s',%d)" % (chipid,c,vendid))    
                    cur.execute("insert into chips values(%d,'%s',%d)" % (chipid,c,vendid))

                    #print(th["vendors"][v][c]["peripherals"])
                    for s in th["vendors"][v][c]["segments"].keys():
                        cur.execute("insert into segments values(%d,%d,%d)" % ( segid,th["vendors"][v][c]["segments"][s][0],th["vendors"][v][c]["segments"][s][1]))
                        cur.execute("insert into chip_segments values(%d,%d)" % ( segid,chipid))
                        segid+=1
                        

                    cur.execute("insert into chip_segments values(%d,%d)" % ( segid,chipid))

                    for p in th["vendors"][v][c]["peripherals"].keys():
                        cur.execute("insert into peripherals values('%s',%d,%d)" % (th["vendors"][v][c]["peripherals"][p]["name"],perid,p))
                        cur.execute("insert into chip_peripherals values(%d,%d)" % (chipid,perid))                            
                        for r in th["vendors"][v][c]["peripherals"][p]["registers"].keys():
                            #print(r, th["vendors"][v][c]["peripherals"][p]["registers"][r])
                            cur.execute("insert into registers values('%s',%d,%d,%d,%d,%d)" %
                                        (
                                            th["vendors"][v][c]["peripherals"][p]["registers"][r]["name"],
                                            regid,
                                            th["vendors"][v][c]["peripherals"][p]["registers"][r]["offset"],
                                            r,
                                            th["vendors"][v][c]["peripherals"][p]["registers"][r]["initval"],
                                            th["vendors"][v][c]["peripherals"][p]["registers"][r]["size"]
                                        )
                            )
                            cur.execute("insert into peripheral_registers values(%d,%d)" % (perid,regid))

                            for b in th["vendors"][v][c]["peripherals"][p]["registers"][r]["fields"].keys():

                                #print("inserting %s %s " %( th["vendors"][v][c]["peripherals"][p]["registers"][r]["name"] ,b))

                                if( th["vendors"][v][c]["peripherals"][p]["registers"][r]["fields"][b]["desc"] == None or nodesc):
                                     th["vendors"][v][c]["peripherals"][p]["registers"][r]["fields"][b]["desc"]=""
                                cur.execute("insert into fields values('%s',%d,%d,%d,%d,'%s')" % (
                                    b,
                                    fieldid,
                                    th["vendors"][v][c]["peripherals"][p]["registers"][r]["fields"][b]["bitw"],
                                    th["vendors"][v][c]["peripherals"][p]["registers"][r]["fields"][b]["bito"],
                                    th["vendors"][v][c]["peripherals"][p]["registers"][r]["fields"][b]["access"],
                                    th["vendors"][v][c]["peripherals"][p]["registers"][r]["fields"][b]["desc"].replace("'","")
                                ))
                                cur.execute("insert into register_fields values(%d,%d)" % (regid,fieldid))

                                for e in th["vendors"][v][c]["peripherals"][p]["registers"][r]["fields"][b]["enums"]:
                                    if( th["vendors"][v][c]["peripherals"][p]["registers"][r]["fields"][b]["enums"][e]["desc"] == None or nodesc):
                                        th["vendors"][v][c]["peripherals"][p]["registers"][r]["fields"][b]["enums"][e]["desc"]=""
                                    cur.execute("insert into field_enumerated values('%s','%s',%d,%d)" % (
                                        e,
                                        th["vendors"][v][c]["peripherals"][p]["registers"][r]["fields"][b]["enums"][e]["desc"].replace("'",""),
                                        enumfid,
                                        th["vendors"][v][c]["peripherals"][p]["registers"][r]["fields"][b]["enums"][e]["value"]
                                    ))
                                    cur.execute("insert into fields_field_enumerateds values(%d,%d)" % (fieldid,enumfid))
                                    enumfid+=1
                                fieldid+=1
                            regid+=1                                 
                        perid+=1
                chipid+=1
                self.conn.commit()
            vendid +=1

        with open('missing_core_chips.csv', newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                if row[0] in chip_by_name_missing_core:
                    print("correcting ", row[0]                        )
                    for chid in chip_by_name_missing_core[row[0]]:
                        if( row[1] in th["cores"]):
                            #print("insert into core_chips values(%d,%d)" % (th["cores"][row[1]]["dbid"],chid))
                            cur.execute("insert into core_chips values(%d,%d)" % (th["cores"][row[1]]["dbid"],chid))

            self.conn.commit()

    
    def __init__(self, db_path,cmsis_svd_datapath,segment_size):
        self.db_path            = db_path
        self.cmsis_svd_datapath = cmsis_svd_datapath        
        self.data_in_mem        = {}
        self.segment_size = segment_size
        if os.path.isfile(self.db_path):
            self.conn           =sqlite3.connect(self.db_path)
            cur = self.conn.cursor()
            cur.execute("SELECT segsz FROM db_info")
            rows = cur.fetchall()
            db_segment_sz= (rows[0][0])
            if(db_segment_sz != segment_size):
                print("This database is built for a segment size of '0x%08x' please use another db or size" % (db_segment_sz), file=sys.stderr)
                exit()
        else:
            self.conn           =sqlite3.connect(self.db_path)
            #non existing db file, rebuild it
            self.build_db_skel()
