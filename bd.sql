create table vendors (
       id INT PRIMARY KEY NOT NULL,
       vendor text not null
);

create table chips (
       id INT PRIMARY KEY NOT NULL,
       chip text not null,
       vendorid int not null,
       foreign key(vendorid) references vendors(id)
);

create table  segments (
       id INT PRIMARY KEY NOT NULL,
       addr_start int not null,
       addr_end   int not null
);

create table chip_segments (
       sid int not null,
       cid int not null,
       foreign key(cid) references chips(id),
       foreign key(sid) references segments(id),
       PRIMARY KEY (cid,sid)
);


create table db_info (
       generated int not null,
       segsz int,
       PRIMARY KEY (segsz)
);

create table peripherals (
       name text unique not null,
       id int unique not null,
       base_address int not null,
       cid not null,
       foreign key(cid) references chips(id),
       PRIMARY KEY (cid,base_address)

);
