# -*- coding: utf-8 -*-


import csv
import pandas
import nibabel as nib
import numpy as np
from .utils import run_shell


def maskFromAtlas(atlasPath, indices, output):
    # input
    atlas = nib.load(atlasPath)
    atlasData = atlas.get_data()
    maskData = np.empty_like(atlasData)

    # compute mask
    for val in indices:
        maskData[atlasData == val] = 1

    # save
    nib.Nifti1Image(
            maskData,
            atlas.affine,
            atlas.header,
            ).to_filename(output)

    return output


def computeSuvr(input, mask, output):
    # input
    image = nib.load(input)
    data = image.get_data()
    maskData = nib.load(mask).get_data()

    # compute SUVR
    refData = np.ma.masked_where(maskData==0, data, copy=True)
    suvrData = data / np.nanmean(refData)

    # save
    nib.Nifti1Image(
            suvrData,
            image.affine,
            image.header,
            ).to_filename(output)

    return output


class ImgStatsFromAtlas(object):

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

    def __init__(self, img, atlas, output):
        self.img = img
        self.atlas = atlas

        self.outputDefault = "default.stats"
        self.outputSpecial = "special.stats"
        self.output = output

    def computeDefault(self):
        cmd = "mri_segstats --ctab-default --excludeid 0 --i {0} --seg {1} --sum {2}"
        run_shell(cmd.format(self.img, self.atlas, self.outputDefault))

    def computeSpecial(self):
        volData = nib.load(self.img).get_data()
        atlasData = nib.load(self.atlas).get_data()

        stats = [['StructName', 'mean', 'std', 'min', 'max', 'range']]
        for structName, values in self.USER_LABELS.items():
            mask = np.zeros_like(atlasData)
            for value in values:
                mask[atlasData==value] = 1

            data = np.ma.masked_where(mask==0, volData, copy=True)

            stats.append([
                structName,
                float("{0:.4f}".format(np.nanmean(data))),
                float("{0:.4f}".format(np.nanstd(data))),
                float("{0:.4f}".format(np.nanmin(data))),
                float("{0:.4f}".format(np.nanmax(data))),
                float("{0:.4f}".format(np.nanmax(data)-np.nanmin(data))),
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
        mergeData.to_csv(self.output, sep="\t", index=False)

    def compute(self):
        self.computeDefault()
        self.computeSpecial()
        self.mergeResults()
        run_shell("rm {}".format(self.outputDefault))
        run_shell("rm {}".format(self.outputSpecial))


class CentiloidStats(object):

    SCALE = {
        # DOI:10.1016/j.jalz.2014.07.003
        "PIB": {
            "CerebGry": {"YC": 1.170, "AD": 2.428},
            "WhlCbl": {"YC": 1.009, "AD": 2.076},
            "WhlCblBrnStm": {"YC": 0.959, "AD": 1.962},
            "Pons": {"YC": 0.761, "AD": 1.535},
        },
        # DOI:10.2967/jnumed.115.171595
        "NAV": {
            "CerebGry": False,
            "WhlCbl": {"YC": 1.028, "AD": 2.202},
            "WhlCblBrnStm": False,
            "Pons": False,
        },
    }

    def __init__(self, input, tracer, roiName, output):
        self.input = input
        self.tracer = tracer
        self.roiName = roiName
        self.output = output


    @property
    def scale(self):
        scaleDict = self.SCALE.get(self.tracer)
        if scaleDict:
            return scaleDict[self.roiName]
        else:
            return False


    def compute(self):
        img = nib.load(self.input)

        # compute Centiloid
        if self.scale:
            numerator = (img.get_data() - self.scale["YC"]) * 100
            denominator = self.scale["AD"] - self.scale["YC"]
            centiloidData = numerator / denominator
            save = True
        else:
            centiloidData = None
            save = False

        if save:
            nib.Nifti1Image(
                    centiloidData,
                    img.affine,
                    img.header,
                    ).to_filename(self.output)

def meanFromRoi(img, roi):
    try:
        data = nib.load(img).get_data()
    except:
        return "n/a"

    maskData = nib.load(roi).get_data()
    dataM = np.ma.masked_where(maskData==0, data, copy=True)
    return "{0:.4f}".format(np.nanmean(dataM))

