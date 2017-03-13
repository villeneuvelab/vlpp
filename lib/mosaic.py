# -*- coding: utf-8 -*-


import matplotlib
import matplotlib.pyplot as plt
import nibabel as nb
import numpy as np
import os


def boundingBox(vol):
    r = np.any(vol, axis=(1, 2))
    c = np.any(vol, axis=(0, 2))
    z = np.any(vol, axis=(0, 1))

    rmin, rmax = np.where(r)[0][[0, -1]]
    cmin, cmax = np.where(c)[0][[0, -1]]
    zmin, zmax = np.where(z)[0][[0, -1]]

    return rmin, rmax, cmin, cmax, zmin, zmax


def generate_lut_data():
    """
    Return `norm` and `cmap` with matplotlib from FreeSurferColorLUT.txt
    """
    fsColorLut = os.path.join(
            os.getenv('FREESURFER_HOME'), 'FreeSurferColorLUT.txt')
    data = np.genfromtxt(
            fsColorLut, usecols=[0, 2, 3, 4], dtype=np.int)

    #colors = np.zeros((data[-1,0]+1, data.shape[1]))
    #colors[:,0] = range(0, data[-1,0]+1, 1)
    #colors[data[:,0],1:] = data[:,1:]

    colors = data

    cmap = matplotlib.colors.ListedColormap(colors[:,1:]/256)
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
            mask=None, contour= None, overlay=None,
            vmin=None, vmax=None, cmap=None,
            ):
        self.in_file = in_file
        self.volume = nb.load(in_file).get_data()
        self.out_file = out_file
        self.mask = mask
        self.contour = contour
        self.overlay = overlay
        self._vmin = vmin
        self._vmax = vmax
        self._cmap = cmap
        self.overlay = None
        self.volWidth = None
        self.volHeight = None

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


    def save(self, target):
        """
            target : link of the output image
        """
        mosaicData = self._computeMosaic()

        # Figure Setup
        dpi = 100
        figsize = (mosaicData.shape[1] / dpi, mosaicData.shape[0] / dpi)
        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)

        # Volume
        ax.imshow(mosaicData, vmin=self.vmin, vmax=self.vmax, cmap=self.cmap)

        # Contour
        if self.contour is not None:
            contour = self._computeMosaic(nb.load(self.contour).get_data())
            plt.contour(contour, [0], colors='r')

        # Overlay
        if self.overlay is not None:
            norm, cmap = generate_lut_data()
            overlay = self._computeMosaic(nb.load(self.overlay).get_data())
            overlay = np.ma.masked_where(overlay == 0, overlay)
            ax.imshow(overlay, alpha=0.6, norm=norm, cmap=cmap)

        fig.savefig(target, facecolor='black', dpi=dpi)
        plt.close()

        tags = {
                'mosaic_file': os.path.basename(target),
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

        #data3D = np.rot90(data3D, 2)
        #data3D = data3D.transpose((0, 2, 1))
        #self.vol = np.swapaxes(self.vol, 1, 2)

        if recordWH:
            self.volWidth = data3D.shape[2]
            self.volHeight = data3D.shape[1]

        slicesNumber = len(data3D)
        sq = int(np.ceil(np.sqrt(slicesNumber)))

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
                    np.nan * np.ones((height, width_margin))
                    ])
            im = np.concatenate([im, this_im], 0)

        #return np.rot90(im, 2)
        return im

