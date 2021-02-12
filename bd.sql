-- the day i catch the dev that desided no to put autoindexes
-- on foreign keys in SQLite i hit him in the face
-- not hard
-- but with a lot of spite

PRAGMA foreign_keys = ON;

create table cores (
       id int primary key not null,
       name text not null
);
create index cn on cores (name);

create table vendors (
       id INT primary key not null,
       vendor text unique not null
);

create table chips (
       id INT primary key not null,
       chip text not null,
       vendorid int not null,
       foreign key(vendorid) references vendors(id)
);
create index cv on chips (vendorid);

create table core_chips (
       coid INT not null,
       chid INT not null,
       foreign key(coid) references cores(id),
       foreign key(chid) references chips(id),
       primary key (coid,chid)
);
create index cocco on  core_chips (coid);
create index cocch on  core_chips (chid);


create table  segments (
       id INT primary key not null,
       addr_start int not null,
       addr_end   int not null
);
create table core_segments (
       sid int not null,
       cid int not null,
       foreign key(cid) references cores(id),
       foreign key(sid) references segments(id),
       primary key (cid,sid)
);
create index coss on  core_segments (sid);
create index cosc on  core_segments (cid);

create table chip_segments (
       sid int not null,
       cid int not null,
       foreign key(cid) references chips(id),
       foreign key(sid) references segments(id),
       primary key (cid,sid)
);
create index css on  chip_segments (sid);
create index csc on  chip_segments (cid);

create table db_info (
       generated int not null,
       segsz int,
       primary key (segsz)
);

create table peripherals (
       name text not null,
       id int not null,
       base_address int ,
       primary key (id)

);

create table core_peripherals(
       cid not null,	
       pid not null,		  
       foreign key(pid) references peripherals(id),
       foreign key(cid) references cores(id)
       primary key (cid,pid)	   
);
create index copc on core_peripherals (cid);
create index copp on core_peripherals (pid);

create table chip_peripherals (
       cid not null,
       pid not null,		  
       foreign key(pid) references peripherals(id),
       foreign key(cid) references chips(id)
       primary key (cid,pid)	   

);
create index cpc on chip_peripherals (cid);
create index cpp on chip_peripherals (pid);

create table field_enumerated (
       name text not null,
       description text,
       id int not null,
       value int not null,
       primary key (id)
);

create table fields (
       name text not null,
       id int not null,
       bitw int not null,
       offset int,
       access int,
       description text,
       primary key (id)
);
create index foff on fields  (offset);

create table fields_field_enumerateds (
fid int not null,
eid int not null,
foreign key(eid) references field_enumerated(id),
foreign key(fid) references fields(id),
primary key (eid,fid)
);
create index feeid on fields_field_enumerateds (fid);
create index fefid on fields_field_enumerateds (eid);



create table registers (
       name text not null,
       id int not null,
       offset int ,
       address int ,	
       initval int,
       sz int not null,
       primary key (id)
);
create index rrs on registers (sz);
create index rro on registers (offset);

create table register_fields (
rid int not null,
fid int not null,
foreign key(rid) references registers(id),
foreign key(fid) references fields(id),
primary key (rid,fid)
);
create index frrid on register_fields (fid);
create index frfid on register_fields (rid);

create table peripheral_registers (
       pid not null,
       rid not null,		  
       foreign key(pid) references peripherals(id),
       foreign key(rid) references registers(id),
       primary key (rid,pid)	   
);
create index prr on peripheral_registers (rid);
create index prp on peripheral_registers (pid);


