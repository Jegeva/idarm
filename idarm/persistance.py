from .utils import utils
import os
import sqlite3
import time

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



            
    def restore_chip(self,th,v,chip):
        cur = self.conn.cursor()
        if ( v not in th):
            th["vendors"][v] = {}
        cur.execute("SELECT id,chip FROM chips where chip='%s'" % (chip))
        rows_c = cur.fetchall()
        for row_c in rows_c:

            chipid = row_c[0]
            c = row_c[1]
            #print("restoring %d %s" % (chipid,c))
            th["vendors"][v][c] = {}
            th["vendors"][v][c]["peripherals"] = {}
            th["vendors"][v][c]["db_id"] = chipid
            th["vendors"][v][c]["segments"] = {}
            th["vendors"][v][c]["dirty"] = False
            
            cur.execute("SELECT addr_start,addr_end FROM segments, chip_segments where segments.id=chip_segments.sid and chip_segments.cid=%d" % (chipid))                
            rows_s = cur.fetchall()
            for row_s in rows_s:
                k = "%d-%d" % (row_s[0],row_s[1])
                th["vendors"][v][c]["segments"][k] = [row_s[0],row_s[1]]
            
            cur.execute("SELECT pid,name,base_address FROM peripherals, chip_peripherals where peripherals.id=chip_peripherals.pid and chip_peripherals.cid=%d" % (chipid))                
            rows_p = cur.fetchall()
            for row_p in rows_p:
                periphid = row_p[0]
                baddr    = row_p[2]
                th["vendors"][v][c]["peripherals"][baddr] = {}
                th["vendors"][v][c]["peripherals"][baddr]["name"] = row_p[1]
                th["vendors"][v][c]["peripherals"][baddr]["db_id"] = periphid
                th["vendors"][v][c]["peripherals"][baddr]["registers"] = {}
                cur.execute("SELECT rid,name,offset,address,initval,sz FROM registers, peripheral_registers where registers.id=peripheral_registers.rid and peripheral_registers.pid=%d" % (periphid))                
                rows_r = cur.fetchall()
                for row_r in rows_r:
                    raddr = row_r[3]
                    th["vendors"][v][c]["peripherals"][baddr]["registers"][raddr] = {}
                    th["vendors"][v][c]["peripherals"][baddr]["registers"][raddr]["db_id"] = row_r[0]
                    th["vendors"][v][c]["peripherals"][baddr]["registers"][raddr]["name"]  = row_r[1]
                    th["vendors"][v][c]["peripherals"][baddr]["registers"][raddr]["offset"]= row_r[2]
                    th["vendors"][v][c]["peripherals"][baddr]["registers"][raddr]["address"]= raddr
                    th["vendors"][v][c]["peripherals"][baddr]["registers"][raddr]["initval"]= row_r[4]
                    th["vendors"][v][c]["peripherals"][baddr]["registers"][raddr]["sz"]= row_r[5]

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
        cur.execute("SELECT vendor FROM vendors")
        rows_v = cur.fetchall()
        for row_v in rows_v:
            vendor = row_v[0]
            self.restore_vendor(th,vendor)

    def persist(self,th):
        vendid = 0
        chipid = 0
        perid  = 0
        regid  = 0
        segid = 0
        cur = self.conn.cursor()
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


                    #print("insert into chips values(%d,'%s',%d)" % (chipid,c,vendid))    
                    cur.execute("insert into chips values(%d,'%s',%d)" % (chipid,c,vendid))
                    #print(th["vendors"][v][c]["peripherals"])
                    for s in th["vendors"][v][c]["segments"].keys():
                        cur.execute("insert into segments values(%d,%d,%d)" % ( segid,th["vendors"][v][c]["segments"][s][0],th["vendors"][v][c]["segments"][s][1]))
                        cur.execute("insert into chip_segments values(%d,%d)" % ( segid,chipid))
                        segid+=1
                        
                        
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
                                            0
                                        )
                            )
                            cur.execute("insert into peripheral_registers values(%d,%d)" % (perid,regid))         
                            regid+=1                                 
                        perid+=1
                chipid+=1
                self.conn.commit()
            vendid +=1
    
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
