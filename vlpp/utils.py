# -*- coding: utf-8 -*-


import os
import json
import shlex
import shutil
import subprocess
from jinja2 import Environment, FileSystemLoader


PKG_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL_PATH = os.path.join(PKG_PATH, "templates")


def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def add_suffix(path, suffix, ext=None):
    root, _ext = splitext_(os.path.basename(path))

    if not suffix.startswith("_"):
        suffix = "_" + suffix

    if ext is not None:
        return root + suffix + ext
    else:
        return root + suffix + _ext


def splitext_(path):
    for ext in ['.nii.gz']:
        if path.endswith(ext):
            return path[:-len(ext)], path[-len(ext):]
    return os.path.splitext(path)


def gzipd(path):
    root, ext = splitext_(path)

    source = path
    if os.path.islink(path):
        source = root + "_copy"  + ext
        shutil.copy(path, source)

    run_shell("gzip -d {0}".format(source))

    return source.replace(".gz", "")


def run_shell(commandLine):

    cmd = shlex.split(commandLine)

    try:
        process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = process.communicate()

        #try:
            #logger.info("\n" + output.decode("utf-8"))
        #except:
            #logger.info(output)

    except OSError as exception:
        print("Exception: {}".format(exception))

    return output


def get_jinja_tpl(templatePath):
    path, templateName  = os.path.split(templatePath)

    return Environment(
            loader=FileSystemLoader(path or "./"),
            trim_blocks=True,
            ).get_template(templateName)


def run_matlab(templatePath, tags, filename):
    get_jinja_tpl(templatePath).stream(**tags).dump(filename)
    print(run_shell("matlab -nodisplay < {0}".format(filename)))


def nfmap2dict(mapStr):
    rsl = {}
    for item in mapStr[1:-1].replace(" ", "").split(","):
        it = item.split(":")
        rsl[it[0]] = it[1]
    return rsl


def filename2dict(filename):
    rsl = {}
    base, _ = splitext_(filename)
    for item in base.split("_"):
        it = item.split("-")
        try:
            rsl[it[0]] = it[1]
        except:
            rsl[it[0]] = None
    return rsl


def warn(messages):
    for line in messages:
        print(line)
