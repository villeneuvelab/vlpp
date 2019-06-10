# -*- coding: utf-8 -*-


import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nibabel as nb
import numpy as np
import os
import sys


def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def boundingBox(vol):
    r = np.any(vol, axis=(1, 2))
    c = np.any(vol, axis=(0, 2))
    z = np.any(vol, axis=(0, 1))

    rmin, rmax = np.where(r)[0][[0, -1]]
    cmin, cmax = np.where(c)[0][[0, -1]]
    zmin, zmax = np.where(z)[0][[0, -1]]

    return rmin, rmax, cmin, cmax, zmin, zmax


def generate_lut_data(suit=False):
    """
    Return `norm` and `cmap` with matplotlib from FreeSurferColorLUT.txt
    """
    fsColorLut = os.path.join(
            os.environ["VL_QUARANTINE_DIR"], 'Core', 'freesurfer', '6.0.0', 'FreeSurferColorLUT.txt')
    data = np.genfromtxt(
            fsColorLut, usecols=[0, 2, 3, 4], dtype=np.int)

    #colors = np.zeros((data[-1,0]+1, data.shape[1]))
    #colors[:,0] = range(0, data[-1,0]+1, 1)
    #colors[data[:,0],1:] = data[:,1:]

    if suit:
        suitColorLut = os.path.join(
                os.environ["VL_QUARANTINE_DIR"], "Core", "matlab_toolboxes", "spm12",
                "spm_toolboxes", "suit", "v3.2",
                "atlas", "Cerebellum-SUIT.nii.txt")
        suitData = np.genfromtxt(suitColorLut, usecols=[0,2], dtype=np.int)
        colors = data
    else:
        colors = data

    cmap = matplotlib.colors.ListedColormap(colors[:,1:]/256.)
    norm = matplotlib.colors.BoundaryNorm(colors[:,0], cmap.N)
    return norm, cmap


def create_index(tags, target):
    from jinja2 import Environment, FileSystemLoader
    #templateDir = os.path.join('templates')
    templateDir = '/home/chris/local/vlpp-dev/templates'
    jinja2Env = Environment(
            loader=FileSystemLoader(templateDir), trim_blocks=True)
    tpl = jinja2Env.get_template('index.tpl')
    htmlCode = tpl.render(**tags)
    with open(target, 'w') as f:
        f.write(htmlCode)


class Mosaic(object):

    def __init__(
            self, in_file, out_file=None,
            mask=None, contour=None, overlay=None,
            vmin=None, vmax=None, cmap=None, rot=0,
            ):
        self.in_file = in_file
        try: self.volume = nb.load(in_file).get_data()
        except: return
        self.out_file = out_file
        self.mask = mask
        self.contour = contour
        self.overlay = overlay
        self._vmin = vmin
        self._vmax = vmax
        self._cmap = cmap
        self.volWidth = None
        self.volHeight = None
        self.rot = rot

    @property
    def vmin(self):
        if self._vmin is None:
            return np.nanmin(self.volume)
        else:
            return self._vmin
    @vmin.setter
    def vmin(self, value):
        self._vmin = value

    @property
    def vmax(self):
        if self._vmax is None:
            return np.nanmax(self.volume)
        else:
            return self._vmax
    @vmax.setter
    def vmax(self, value):
        self._vmax = value

    @property
    def cmap(self):
        CMAP = {
                "gray": plt.cm.gray,
                "viridis": plt.cm.viridis,
                }
        if self._cmap is None:
            return CMAP['viridis']
        else:
            if self._cmap in CMAP:
                return CMAP[self._cmap]
            else:
                return CMAP['viridis']

    @cmap.setter
    def cmap(self, value):
        self._cmap = value


    def save(self, target, suit=False):
        """
            target : link of the output image
        """
        if self.in_file == None:
            return {'X':98, 'Y':134, 'Z':72}

        mosaicData = self._computeMosaic()

        # Figure Setup
        dpi = 100.
        figsize = (mosaicData.shape[1]/(dpi*10), mosaicData.shape[0]/(dpi*10))
        fig = plt.figure(figsize=figsize, dpi=dpi)
        #fig = plt.figure()
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)

        # Volume
        ax.imshow(mosaicData, vmin=self.vmin, vmax=self.vmax, cmap=self.cmap)

        # Contour
        if self.contour is not None:
            contour = self._computeMosaic(nb.load(self.contour).get_data())
            plt.contour(contour, [0], colors='r', linewidths=0.1, linestyles=None)

        # Overlay
        if self.overlay is not None:
            norm, cmap = generate_lut_data(suit)
            overlay = self._computeMosaic(nb.load(self.overlay).get_data())
            overlay = np.ma.masked_where(overlay == 0, overlay)
            ax.imshow(overlay, alpha=0.5, norm=norm, cmap=cmap)

        fig.savefig(target, facecolor='black', dpi=dpi*10)
        #fig.savefig(target, facecolor='black')
        plt.close()

        tags = {
            'X': (mosaicData.shape[1]/self.volWidth)*(mosaicData.shape[0]/self.volHeight)+2,
            'Y': self.volWidth,
            'Z': self.volHeight,
            }
        #create_index(tags, os.path.splitext(target)[0]+'.html')
        return tags


    def _computeMosaic(self, volume=None):
        if volume is None:
            volume = self.volume
            recordWH = True
        else:
            recordWH = False

        # Crop the volume with a mask
        if self.mask is None:
            data3D = volume
        else:
            maskData = nb.load(self.mask).get_data()
            minmax = boundingBox(maskData)
            data3D = volume[
                    minmax[0]:minmax[1],
                    minmax[2]:minmax[3],
                    minmax[4]:minmax[5],
                    ]

        #data3D = data3D.transpose((0, 2, 1))
        #self.vol = np.swapaxes(self.vol, 1, 2)

        slicesNumber = len(data3D)
        sq = int(np.ceil(np.sqrt(slicesNumber)))

        if recordWH:
            self.volX = sq ** 2
            self.volWidth = data3D.shape[2]
            self.volHeight = data3D.shape[1]

        # First line
        stop = sq
        im = np.hstack(data3D[0:stop])
        height = im.shape[0]
        width = im.shape[1]

        while stop < slicesNumber:
            start = stop
            stop += sq
            if stop > slicesNumber : stop = slicesNumber

            this_im = np.hstack(data3D[start:stop])
            width_margin = width - this_im.shape[1]

            if width_margin > 0:
                this_im = np.hstack([
                    this_im,
                    #np.nan * np.ones((height, width_margin))
                    np.zeros((height, width_margin))
                    ])
            im = np.concatenate([im, this_im], 0)

        if self.rot == 0:
            return im
        else:
            return np.rot90(im, self.rot)


def main():
    in_file = "${subject.anat}"
    mask_file = "{mask_file}"
    contour_file = "{contour_file}"
    overlay_file = "{overlay_file}"
    cmap = "{cmap}"

    m = Mosaic(in_file)
    if mask_file == "null": m.mask = mask_file
    if contour_file == "null": m.contour = contour_file
    if overlay_file == "null": m.overlay = overlay_file
    if cmap == "null": m.cmap = cmap

    tag = m.save("mosaic.jpg")
    tag.update({
        'title': "", #self.inputs.title,
        'notes': "", #self.inputs.notes,
        'canvas_id': "", #'canvas_{}'.format(suffix),
        'sprite': "", #'sprite_{}'.format(suffix),
        })

    #create_index(tags, "mosaic.html")

