# -*- coding: utf-8 -*-


import os

from .utils import load_json, get_jinja_tpl, TPL_PATH
from operator import itemgetter


class Dashboards(object):

    def __init__(self, jsonPaths, tags):
        self.jsonPaths = jsonPaths
        self.tags = tags

    def run(self, _type, dashTags):
        # Usefull directories
        os.mkdir("data")

        # Get jsons information
        participants = []
        for j in self.jsonPaths:
            participants.append(load_json(j))
        self.tags["participants"] = sorted(
                participants, key=itemgetter('participant_id'))

        # Save javascript data
        self.tags["dashTags"] = dashTags
        dataJsTpl = os.path.join(TPL_PATH, "qa_dataSubjects.js")
        dataJsPath = "./data/dataSubjects_{}.js".format(_type)
        get_jinja_tpl(dataJsTpl).stream(**self.tags).dump(dataJsPath)

        # Save Dashboard
        self.tags["dataSubjects"] = dataJsPath
        dashTpl = os.path.join(TPL_PATH, "qa_registrations.html")
        htmlPath = "registration_{}.html".format(_type)
        get_jinja_tpl(dashTpl).stream(**self.tags).dump(htmlPath)


def anat_dash(jsonPaths):
    tags = {
            "infos": [
                {
                    "tag": "anat",
                    "title": "T1",
                    "notes": "Freesufer T1 in native space",
                },
                {
                    "tag": "atlas",
                    "title": "T1 and aparc+aseg",
                    "notes": "Freesufer T1 in native space with aparc+aseg as overlay",
                },
                {
                    "tag": "pet",
                    "title": "PET",
                    "notes": "PET image in freesurfer native space",
                },
                {
                    "tag": "petatlas",
                    "title": "PET and aparc+aseg",
                    "notes": "PET image in freesurfer native space with aparc+aseg as overlay",
                },
                ],
            }

    dashTags = ["anat", "atlas", "pet", "petatlas"]
    dash = Dashboards(jsonPaths, tags)
    dash.run("T1w", dashTags)


def tpl_dash(jsonPaths):
    tags = {
            "infos": [
                {
                    "tag": "centctx",
                    "title": "Centiloid Std VOI",
                    "notes": "PET image in MNI space with VOI ctx",
                },
                {
                    "tag": "centCerebGry",
                    "title": "Centiloid Std VOI",
                    "notes": "PET image in MNI space with VOI CerebGry",
                },
                {
                    "tag": "centPons",
                    "title": "Centiloid Std VOI",
                    "notes": "PET image in MNI space with VOI Pons",
                },
                {
                    "tag": "centWhlCblBrnStm",
                    "title": "Centiloid Std VOI",
                    "notes": "PET image in MNI space with VOI WhlCblBrnStm",
                },
                {
                    "tag": "centWhlCbl",
                    "title": "Centiloid Std VOI",
                    "notes": "PET image in MNI space with VOI WhlCbl",
                },
                ],
            }

    dashTags = [
            "centCerebGry",
            "centPons",
            "centWhlCblBrnStm",
            "centWhlCbl",
            "centctx",
            ]
    dash = Dashboards(jsonPaths, tags)
    dash.run("tpl", dashTags)
