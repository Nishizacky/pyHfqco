- [ZPSQt\_jtl](#zpsqt_jtl)
- [HFQ\_JTL2\_IN](#hfq_jtl2_in)
- [ZZPSQ\_jtl\_0](#zzpsq_jtl_0)
- [ZZPSQ\_jtl\_1](#zzpsq_jtl_1)
- [ZZPSQ\_ijtl](#zzpsq_ijtl)
- [ZZPSQ\_sink](#zzpsq_sink)
- [hfq\_ijtl](#hfq_ijtl)
- [hfq\_sink](#hfq_sink)
- [hfq\_jtl](#hfq_jtl)

*JSIM model
.model jjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA)
.model jjmod_pi jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA, PHI=PI)
# ZPSQt_jtl
.subckt ZPSQ_IN_jtl          1    10
***       Pin
L4                 2         10   0.200pH fcheck
L3                 3         10   0.200pH fcheck
L1                 1         4   1.550pH fcheck
L0                 5         1   1.550pH fcheck
B1                 4         3  jjmod_pi area=0.608
RS1                4         3   12.71ohm
B0                 5         2  jjmod area=0.608
RS0                5         2   12.71ohm
.ends

# HFQ_JTL2_IN
.subckt HFQ_JTL2_IN          1          5        13
***       Pin      Pout
X2         ZPSQ_IN_jtl           8     0
X1         ZPSQ_IN_jtl           7     0
*L6                 8         9   2.600pH fcheck
L5                10        11   2.600pH fcheck
L4                 8         5   1.83pH fcheck
*L3                 8         6   1.000pH fcheck
L2                 7         8   5.66pH fcheck
L1                10         7   2.83pH fcheck
L0                 1        10   1.0pH fcheck
*R1                13         9   115.15ohm
R0                13        11   60ohm
.ends

.subckt dchfq_squid1   1    10
***       Pin
L4                 2         10   0.200pH fcheck
L3                 3         10   0.200pH fcheck
L1                 1         4   1.550pH fcheck
L0                 5         1   1.550pH fcheck
B1                 4         3   jjmod_pi area=0.65
RS1                4         3   12.71ohm
B0                 5         2   jjmod area=0.65
RS0                5         2   12.71ohm
.ends

.subckt dchfq_squid2   1    10 
***       Pin
L4                 2         10   0.200pH fcheck
L3                 3         10   0.200pH fcheck
L1                 1         4   1.550pH fcheck
L0                 5         1   1.550pH fcheck
B1                 4         3  jjmod_pi area=0.59
RS1                4         3   12.71ohm
B0                 5         2  jjmod area=0.59
RS0                5         2   12.71ohm
.ends

.subckt dchfq        1       9       100
R1                      1       2       400ohm
L1                      2       0       50pH
L2                      2       3       1pH
X1      dchfq_squid1    3       4
L3                      4       5       1pH
X2      dchfq_squid2    5       0
L4                      5       6       1pH
L5                      5       7       4.6pH
X3      ZPSQ_IN_jtl       7       0
L6                      7       8       5.66pH
X4      ZPSQ_IN_jtl       8       0
L7                      8       9       1.83pH
R2                      5       100     72ohm
.ends


.subckt pi_2shifter             1           2
***    Pin    Pout
L1      1       3           1.400pH fcheck
L0      1       2           0.200pH fcheck
B0      3       2           jjmod_pi area=20
.ends
# ZZPSQ_jtl_0
.subckt ZZPSQ_jtl_0          1          2
***       Pin      Pout
L4                 3         2   0.200pH fcheck
L3                 4         2   0.200pH fcheck
L1                 1         5   1.400pH fcheck
L0                 1         6   1.400pH fcheck
B2                 5         7  jjmod_pi area=20
RS2                5         7   0.20ohm *SHUNT=7.73
B1                 7         4  jjmod area=0.6
RS1                7         4  12.71ohm *SHUNT=7.73
B0                 6         3  jjmod area=0.6
RS0                6         3  12.71ohm *SHUNT=7.73
.ends
# ZZPSQ_jtl_1
.subckt ZZPSQ_jtl_1          1          2
***       Pin      Pout
L4                 3         2   0.200pH fcheck
L3                 4         2   0.200pH fcheck
L1                 1         5   1.400pH fcheck
L0                 1         6   1.400pH fcheck
B2                 5         7  jjmod_pi area=20
RS2                5         7   0.20ohm *SHUNT=7.73
B1                 7         4  jjmod area=0.6
RS1                7         4  12.71ohm *SHUNT=7.73
B0                 6         3  jjmod area=0.6
RS0                6         3  12.71ohm *SHUNT=7.73
.ends
# ZZPSQ_ijtl
.subckt ZZPSQ_ijtl          1          2
***       Pin      Pout
L4                 3         2   0.200pH fcheck
L3                 4         2   0.200pH fcheck
L1                 1         5   1.400pH fcheck
L0                 1         6   1.400pH fcheck
B2                 5         7  jjmod_pi area=20
RS2                5         7   0.20ohm *SHUNT=7.73
B1                 7         4  jjmod area=0.6
RS1                7         4  12.71ohm *SHUNT=7.73
B0                 6         3  jjmod area=0.6
RS0                6         3  12.71ohm *SHUNT=7.73
.ends
# ZZPSQ_sink
.subckt ZZPSQ_sink          1          2
***       Pin      Pout
L4                 3         2   0.200pH fcheck
L3                 4         2   0.200pH fcheck
L1                 1         5   1.400pH fcheck
L0                 1         6   1.400pH fcheck
B2                 5         7  jjmod_pi area=20
RS2                5         7   0.20ohm *SHUNT=7.73
B1                 7         4  jjmod area=0.6
RS1                7         4  12.71ohm *SHUNT=7.73
B0                 6         3  jjmod area=0.6
RS0                6         3  12.71ohm *SHUNT=7.73
.ends

# hfq_ijtl
.subckt hfq_ijtl         46         47
***       din      dout
LP2               26         0   0.198pH fcheck
L2                27        47   1.963pH fcheck
L1                46        27   4.534pH fcheck
XI62            [ZZPSQ_ijtl](ZZPSQ_ijtl)         27         26
.ends

# hfq_sink
.subckt hfq_sink         46        17
***       din
R2                27         0   25.0ohm
R1                17        13   50ohm
LP1               48         0   0.130pH fcheck
L1                30        49   1.172pH fcheck
L2                49        27   2.386pH fcheck
LPR1              13        30   0.177pH fcheck
LPIN              46        30   0.317pH fcheck
XI27            [ZZPSQ_sink](ZZPSQ_sink)         49         48
.ends

# hfq_jtl
.subckt hfq_jtl         46         47        17
***       din      dout
R1                17        13   50ohm
LP1               48         0   0.096pH fcheck
LP2               26         0   0.096pH fcheck
L1                30        49   2.288pH fcheck
L3                27        47   1.963pH fcheck
L2                49        27   4.506pH fcheck
LPR1              13        30   0.177pH fcheck
LPIN              46        30   0.325pH fcheck
XI26            [ZZPSQ_jtl_0](ZZPSQ_jtl_0)         49          4
XI27            [ZZPSQ_jtl_1](ZZPSQ_jtl_1)         27          26
.ends

