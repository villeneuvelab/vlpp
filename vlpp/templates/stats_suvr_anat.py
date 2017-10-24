#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas
import nibabel as nb
from subprocess import call
import numpy as np
import csv


USER_LABELS = {
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


class SuvrStats(object):

    def __init__(self):
        self.suvr = "${suvr}"
        self.atlas = "${atlas}"

        self.outputDefault = "default.stats"
        self.outputSpecial = "special.stats"
        self.output = self.suvr.replace(".nii.gz", ".csv")

    def computeDefault(self):
        cmd = "mri_segstats --ctab-default --excludeid 0 --i {0} --seg {1} --sum {2}"
        call(cmd.format(self.suvr, self.atlas, self.outputDefault), shell=True)

    def computeSpecial(self):
        volData = nb.load(self.suvr).get_data()
        atlasData = nb.load(self.atlas).get_data()

        stats = [['StructName', 'mean', 'std', 'min', 'max', 'range']]
        for structName, values in USER_LABELS.items():
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

        with open(self.outputSpecial, 'wt') as csvfile:
            w = csv.writer(csvfile)#, delimiter=',', quotechar='"')
            w.writerows(stats)

    def mergeResults(self):
        specData = pandas.read_csv(self.outputSpecial)
        data = pandas.read_csv(
                self.outputDefault, delim_whitespace=True, comment="#",
                usecols=[4, 5, 6, 7, 8, 9], names=specData.columns.values)
        mergeData = specData.append(data)
        mergeData.to_csv(self.output)

    def run(self):
        self.computeDefault()
        self.computeSpecial()
        self.mergeResults()


def main():
    app = SuvrStats()
    app.run()

if __name__ == '__main__':
    main()

