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

    # Usefull directories
    os.mkdir("data")

    # Get jsons information
    jsonPaths = "${participant_jsons}"[1:-1].split(", ")
    participants = []
    for j in jsonPaths:
        participants.append(load_json(j))
    tags["participants"] = sorted(participants, key=itemgetter('participant_id'))

    # Save Dashboard
    jinja2Env.get_template('qa_registration_T1w.html').stream(**tags).dump(
            "registration_T1w.html")
    jinja2Env.get_template('qa_dataSubjects.js').stream(**tags).dump(
            "data/dataSubjects.js")

if __name__ == "__main__":
    main()
