''' Present a scatter plot with linked histograms on both axes.

Use the ``bokeh serve`` command to run the example by executing:

    bokeh serve selection_histogram.py

at your command prompt. Then navigate to the URL

    http://localhost:5006/selection_histogram

in your browser.

'''

import numpy as np
import pandas as pd

from bokeh.models import BoxSelectTool, LassoSelectTool, Paragraph
from bokeh.plotting import figure, hplot, vplot

data = pd.read_csv("../test/sample.csv", usecols=['mag_auto_g', 'mag_auto_r', 'mag_auto_i'])

x=data['mag_auto_r']-data['mag_auto_i']
y=data['mag_auto_g']-data['mag_auto_r']


TOOLS="pan,box_select,reset"

# create the scatter plot
p = figure(tools=TOOLS, plot_width=600, plot_height=600, title="g-r vs r-i", min_border=10, min_border_left=50)
r = p.scatter(x, y, size=3, color="#3A5785", alpha=0.1)

p.xaxis.axis_label = 'r-i'
p.yaxis.axis_label = 'g-r'

p.select(BoxSelectTool).select_every_mousemove = False
p.select(LassoSelectTool).select_every_mousemove = False

# create the horizontal histogram
hhist, hedges = np.histogram(x, bins=50)
hzeros = np.zeros(len(hedges)-1)
hmax = max(hhist)*1.1

LINE_ARGS = dict(color="#3A5785", line_color=None)

ph = figure(toolbar_location=None, plot_width=p.plot_width, plot_height=200, x_range=p.x_range,
            y_range=(-hmax, hmax), title=None, min_border=10, min_border_left=50)
ph.xgrid.grid_line_color = None

ph.quad(bottom=0, left=hedges[:-1], right=hedges[1:], top=hhist, color="white", line_color="#3A5785")
hh1 = ph.quad(bottom=0, left=hedges[:-1], right=hedges[1:], top=hzeros, alpha=0.5, **LINE_ARGS)
hh2 = ph.quad(bottom=0, left=hedges[:-1], right=hedges[1:], top=hzeros, alpha=0.1, **LINE_ARGS)

# create the vertical histogram
vhist, vedges = np.histogram(y, bins=50)
vzeros = np.zeros(len(vedges)-1)
vmax = max(vhist)*1.1

th = 42 # need to adjust for toolbar height, unfortunately
pv = figure(toolbar_location=None, plot_width=200, plot_height=p.plot_height+th-10, x_range=(-vmax, vmax),
            y_range=p.y_range, title=None, min_border=10, min_border_top=th)
pv.ygrid.grid_line_color = None
pv.xaxis.major_label_orientation = -3.14/2

pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vhist, color="white", line_color="#3A5785")
vh1 = pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.5, **LINE_ARGS)
vh2 = pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.1, **LINE_ARGS)

pv.min_border_top = 80
pv.min_border_left = 0
ph.min_border_top = 10
ph.min_border_right = 10
p.min_border_right = 10
layout = vplot(hplot(p, pv), hplot(ph, Paragraph(width=200)), width=800, height=800)

def update(attr, old, new):
    inds = np.array(new['1d']['indices'])
    if len(inds) == 0 or len(inds) == len(x):
        hhist1, hhist2 = hzeros, hzeros
        vhist1, vhist2 = vzeros, vzeros
    else:
        neg_inds = np.ones_like(x, dtype=np.bool)
        neg_inds[inds] = False
        hhist1, _ = np.histogram(x[inds], bins=hedges)
        vhist1, _ = np.histogram(y[inds], bins=vedges)
        hhist2, _ = np.histogram(x[neg_inds], bins=hedges)
        vhist2, _ = np.histogram(y[neg_inds], bins=vedges)

    hh1.data_source.data["top"]   =  hhist1
    hh2.data_source.data["top"]   = -hhist2
    vh1.data_source.data["right"] =  vhist1
    vh2.data_source.data["right"] = -vhist2

r.data_source.on_change('selected', update)