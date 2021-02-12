
insert into cores values (0,"M0");
insert into cores values (1,"M0P");
insert into cores values (2,"M1");
insert into cores values (3,"M3");
insert into cores values (4,"M4");
insert into cores values (5,"M7");
insert into cores values (6,"M23");
insert into cores values (7,"M33");
insert into cores values (8,"M35P");
insert into cores values (9,"M55");

-- M0
insert into peripherals values ("SCB1"   ,0, 0xE000E008);
insert into peripherals values ("SYSTICK",1, 0xE000E010);
insert into peripherals values ("NVIC0"  ,2, 0xE000E100);
insert into peripherals values ("SCB0"   ,3, 0xE000ED00);
insert into peripherals values ("NVIC0"  ,4, 0xE000EF00);
--M0P
insert into peripherals values ("MPU"    ,5, 0xE000ED90);
--M4
insert into peripherals values ("FPU"    ,6 ,0xE000EF30);
--M7
insert into peripherals values ("CPUFEAT",7 ,0xE000ED78);
insert into peripherals values ("CMOP"   ,8 ,0xE000EF50);
insert into peripherals values ("ACCON"  ,9 ,0xE000EF90);
--M23
insert into peripherals values ("SAU"    ,10,0XE000ED00);

--SCB1_base (M0)
insert into registers values('CPUID'		,0 ,0		,0		,32);
insert into registers values('ICSR'      	,1 ,0x04	,0         	,32);
insert into registers values('AIRCR'     	,2 ,0x0c	,0xFA050000	,32);
insert into registers values('SCR'       	,3 ,0x10	,0         	,32);
insert into registers values('CCR'       	,4 ,0x14	,0x00000208	,32);
insert into registers values('SHPR2'     	,5 ,0x1c	,0         	,32);
insert into registers values('SHPR3'     	,6 ,0x20	,0         	,32);
-- M0P
insert into registers values('VTOR'       	,7 ,0x08	,0		,32);


--SCB_M3




--SYSTICK
insert into registers values('SYST_CSR'		,7 ,0x00	,0		,32);
insert into registers values('SYST_RVR' 	,8 ,0x04	,0         	,32);
insert into registers values('SYST_CVR'  	,9 ,0x08	,0         	,32);
insert into registers values('SYST_CALIB'	,10,0x0c	,0         	,32);
--NVIC
insert into registers values('ISER'		,11,0		,0		,32);
insert into registers values('ICER'      	,12,0x0080	,0		,32);
insert into registers values('ISPR'      	,13,0x0100	,0		,32);
insert into registers values('ICPR'      	,14,0x0180	,0		,32);
insert into registers values('IPR0'      	,15,0x0300	,0		,32);
insert into registers values('IPR1'	 	,16,0x0304	,0		,32);
insert into registers values('IPR2'	 	,17,0x0308	,0		,32);
insert into registers values('IPR3'	 	,18,0x030c	,0		,32);
insert into registers values('IPR4'	 	,19,0x0310	,0		,32);
insert into registers values('IPR5'	 	,20,0x0314	,0		,32);
insert into registers values('IPR6'	 	,21,0x0318	,0		,32);
insert into registers values('IPR7'	 	,22,0x031c	,0		,32);
--MPU
insert into registers values('MPU_TYPE'		,23,0		,0		,32);
insert into registers values('MPU_CTRL'   	,24,0x04	,0		,32);
insert into registers values('MPU_RNR'	  	,25,0x08	,0		,32);
insert into registers values('MPU_RBAR'	  	,26,0x0C	,0		,32);
insert into registers values('MPU_RASR'	  	,27,0x10	,0		,32);
insert into registers values('MPU_RBAR_A1'	,28,0x14	,0		,32);
insert into registers values('MPU_RASR_A1'	,29,0x18	,0		,32);
insert into registers values('MPU_RBAR_A2'	,30,0x1C	,0		,32);
insert into registers values('MPU_RASR_A2'	,31,0x20	,0		,32);
insert into registers values('MPU_RBAR_A3'	,32,0x24	,0		,32);
insert into registers values('MPU_RASR_A3'	,33,0x28	,0		,32);
--FPU
insert into registers values('CPACR'		,34,0xE000ED88,0,32);
insert into registers values('FPCCR'		,35,0xE000EF34,0,32);
insert into registers values('FPCAR'		,36,0xE000EF38,0,32);
insert into registers values('FPDSCR'		,37,0xE000EF3C,0,32);


insert into core_peripherals values (0,1);
insert into core_peripherals values (0,2);
insert into core_peripherals values (0,3);
insert into core_peripherals values (0,4);
insert into core_peripherals values (0,5);
insert into core_peripherals values (0,6);

insert into core_peripherals values (1,1);
insert into core_peripherals values (1,2);
insert into core_peripherals values (1,3);
insert into core_peripherals values (1,4);
insert into core_peripherals values (1,5);

insert into core_peripherals values (3,0);
insert into core_peripherals values (3,1);
insert into core_peripherals values (3,2);
insert into core_peripherals values (3,3);
insert into core_peripherals values (3,4);
insert into core_peripherals values (3,5);

insert into core_peripherals values (4,0);
insert into core_peripherals values (4,1);
insert into core_peripherals values (4,2);
insert into core_peripherals values (4,3);
insert into core_peripherals values (4,4);
insert into core_peripherals values (4,5);
insert into core_peripherals values (4,6);

insert into core_peripherals values (5,0);
insert into core_peripherals values (5,1);
insert into core_peripherals values (5,2);
insert into core_peripherals values (5,3);
insert into core_peripherals values (5,4);
insert into core_peripherals values (5,5);
insert into core_peripherals values (5,6);
insert into core_peripherals values (5,7);
insert into core_peripherals values (5,8);
insert into core_peripherals values (5,9);

insert into core_peripherals values (6,0);
insert into core_peripherals values (6,1);
insert into core_peripherals values (6,2);
insert into core_peripherals values (6,3);
insert into core_peripherals values (6,4);
insert into core_peripherals values (6,5);
insert into core_peripherals values (6,10);

insert into core_peripherals values (7,0);
insert into core_peripherals values (7,1);
insert into core_peripherals values (7,2);
insert into core_peripherals values (7,3);
insert into core_peripherals values (7,4);
insert into core_peripherals values (7,5);
insert into core_peripherals values (7,10);

