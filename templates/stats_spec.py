#!/usr/bin/env python
# -*- coding: utf-8 -*-


import nibabel as nb
import numpy as np
import csv


volData = nb.load("${suvr}").get_data()
atlasData = nb.load("${atlas}").get_data()

user_labels = {
        "pibindex_Lfrontal": [1003,1012,1014,1018,1019,1020,1027,1028,1032],
        "pibindex_Ltemporal": [1009,1015,1030],
        "pibindex_Lparietal": [1008,1025,1029,1031],
        "pibindex_Lcingulate": [1002,1023,1010,1026],
        "pibindex_Rfrontal": [2003,2012,2014,2018,2019,2020,2027,2028,2032],
        "pibindex_Rtemporal": [2009,2015,2030],
        "pibindex_Rparietal": [2008,2025,2029,2031],
        "pibindex_Rcingulate": [2002,2023,2010,2026],
        "pibindex_Ltemporal_noIT": [1015,1030],
        "pibindex_Rtemporal_noIT": [2015,2030],
        "PIBINDEX_noIT": [1003,1012,1014,1018,1019,1020,1027,1028,1032,1008,
            1025,1029,1031,1002,1023,1010,1026,2003,2012,2014,2018,2019,2020,
            2027,2028,2032,2008,2025,2029,2031,2002,2023,2010,2026,1015,1030,
            2015,2030],
        "PIBINDEX": [1003,1012,1014,1018,1019,1020,1027,1028,1032,1008,1025,
            1029,1031,1002,1023,1010,1026,2003,2012,2014,2018,2019,2020,2027,
            2028,2032,2008,2025,2029,2031,2002,2023,2010,2026,1015,1030,2015,
            2030,2009,1009],
        "MediaPFC": [1014,2014,1028,2028,1026,2026,1002,2002]
        }
stats = [['StructName', 'mean', 'std', 'min', 'max', 'range']]

for structName, values in user_labels.items():
    mask = np.zeros_like(atlasData)
    for value in values:
        mask[atlasData==value] = 1

    data = np.ma.masked_where(mask==0, volData, True)

    stats.append([
        structName,
        float(data.mean()),
        float(data.std()),
        float(data.min()),
        float(data.max()),
        float(data.max()-data.min()),
        ])

with open("summary_user.stats", 'wt') as csvfile:
    w = csv.writer(csvfile)#, delimiter=',', quotechar='"')
    w.writerows(stats)

