#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas

# merge data for ${roiName}
specData = pandas.read_csv("${statsSpec}")
data = pandas.read_csv(
        "${statsDefault}", delim_whitespace=True, comment="#",
        usecols=[4, 5, 6, 7, 8, 9], names=specData.columns.values)
mergeData = specData.append(data)
output = "${participant}_ref-${roiName}_stats.csv"
mergeData.to_csv(output)
