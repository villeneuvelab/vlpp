#!/usr/bin/env python
# -*- coding: utf-8 -*-


import glob
import json
import os
from jinja2 import Environment, FileSystemLoader
from qamosaic import qamosaic

from operator import itemgetter

def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def main():
    # Dashboard template
    templateDir = os.path.join("${workflow.projectDir}", 'templates')
    jinja2Env = Environment(
            loader=FileSystemLoader(templateDir),
            trim_blocks=True,
            )

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

    # Usefull directories
    os.mkdir("data")

    # Get jsons information
    jsonPaths = "${participant_jsons_tpl}"[1:-1].split(", ")
    participants = []
    for j in jsonPaths:
        participants.append(load_json(j))
    tags["participants"] = sorted(participants, key=itemgetter('participant_id'))

    # Save Dashboard
    jinja2Env.get_template('qa_registration_tpl.html').stream(**tags).dump(
            "registration_tpl.html")
    jinja2Env.get_template('qa_dataSubjects_tpl.js').stream(**tags).dump(
            "data/dataSubjects_tpl.js")

if __name__ == "__main__":
    main()
