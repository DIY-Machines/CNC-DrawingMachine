#!/usr/bin/env python
'''
dxf_input.py - input a DXF file >= (AutoCAD Release 13 == AC1012)

Copyright (C) 2008, 2009 Alvin Penner, penner@vaxxine.com
Copyright (C) 2009 Christian Mayer, inkscape@christianmayer.de
- thanks to Aaron Spike for inkex.py and simplestyle.py
- without which this would not have been possible

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''

import inkex, simplestyle, math
from StringIO import StringIO
from urllib import quote

def export_MTEXT():
    # mandatory group codes : (1 or 3, 10, 20) (text, x, y)
    if (vals[groups['1']] or vals[groups['3']]) and vals[groups['10']] and vals[groups['20']]:
        x = vals[groups['10']][0]
        y = vals[groups['20']][0]
        # optional group codes : (21, 40, 50) (direction, text height mm, text angle)
        size = 12                       # default fontsize in px
        if vals[groups['40']]:
            size = scale*vals[groups['40']][0]
        attribs = {'x': '%f' % x, 'y': '%f' % y, 'style': 'font-size: %.1fpx; fill: %s' % (size, color)}
        angle = 0                       # default angle in degrees
        if vals[groups['50']]:
            angle = vals[groups['50']][0]
            attribs.update({'transform': 'rotate (%f %f %f)' % (-angle, x, y)})
        elif vals[groups['21']]:
            if vals[groups['21']][0] == 1.0:
                attribs.update({'transform': 'rotate (%f %f %f)' % (-90, x, y)})
            elif vals[groups['21']][0] == -1.0:
                attribs.update({'transform': 'rotate (%f %f %f)' % (90, x, y)})
        attribs.update({inkex.addNS('linespacing','sodipodi'): '125%'})
        node = inkex.etree.SubElement(layer, 'text', attribs)
        text = ''
        if vals[groups['3']]:
            for i in range (0, len(vals[groups['3']])):
                text += vals[groups['3']][i]
        if vals[groups['1']]:
            text += vals[groups['1']][0]
        found = text.find('\P')         # new line
        while found > -1:
            tspan = inkex.etree.SubElement(node , 'tspan', {inkex.addNS('role','sodipodi'): 'line'})
            tspan.text = text[:found]
            text = text[(found+2):]
            found = text.find('\P')
        tspan = inkex.etree.SubElement(node , 'tspan', {inkex.addNS('role','sodipodi'): 'line'})
        tspan.text = text

def export_POINT():
    # mandatory group codes : (10, 20) (x, y)
    if vals[groups['10']] and vals[groups['20']]:
			if options.gcodetoolspoints:
				generate_gcodetools_point(vals[groups['10']][0], vals[groups['20']][0])
			else:
				generate_ellipse(vals[groups['10']][0], vals[groups['20']][0], w/2, 0.0, 1.0, 0.0, 0.0)

def export_LINE():
    # mandatory group codes : (10, 11, 20, 21) (x1, x2, y1, y2)
    if vals[groups['10']] and vals[groups['11']] and vals[groups['20']] and vals[groups['21']]:
        path = 'M %f,%f %f,%f' % (vals[groups['10']][0], vals[groups['20']][0], scale*(vals[groups['11']][0] - xmin), - scale*(vals[groups['21']][0] - ymax))
        attribs = {'d': path, 'style': style}
        inkex.etree.SubElement(layer, 'path', attribs)

def export_SPLINE():
    # mandatory group codes : (10, 20, 70) (x, y, flags)
    if vals[groups['10']] and vals[groups['20']] and vals[groups['70']]:
        if not (vals[groups['70']][0] & 3) and len(vals[groups['10']]) == 4 and len(vals[groups['20']]) == 4:
            path = 'M %f,%f C %f,%f %f,%f %f,%f' % (vals[groups['10']][0], vals[groups['20']][0], vals[groups['10']][1], vals[groups['20']][1], vals[groups['10']][2], vals[groups['20']][2], vals[groups['10']][3], vals[groups['20']][3])
            attribs = {'d': path, 'style': style}
            inkex.etree.SubElement(layer, 'path', attribs)
        if not (vals[groups['70']][0] & 3) and len(vals[groups['10']]) == 3 and len(vals[groups['20']]) == 3:
            path = 'M %f,%f Q %f,%f %f,%f' % (vals[groups['10']][0], vals[groups['20']][0], vals[groups['10']][1], vals[groups['20']][1], vals[groups['10']][2], vals[groups['20']][2])
            attribs = {'d': path, 'style': style}
            inkex.etree.SubElement(layer, 'path', attribs)

def export_CIRCLE():
    # mandatory group codes : (10, 20, 40) (x, y, radius)
    if vals[groups['10']] and vals[groups['20']] and vals[groups['40']]:
        generate_ellipse(vals[groups['10']][0], vals[groups['20']][0], scale*vals[groups['40']][0], 0.0, 1.0, 0.0, 0.0)

def export_ARC():
    # mandatory group codes : (10, 20, 40, 50, 51) (x, y, radius, angle1, angle2)
    if vals[groups['10']] and vals[groups['20']] and vals[groups['40']] and vals[groups['50']] and vals[groups['51']]:
        generate_ellipse(vals[groups['10']][0], vals[groups['20']][0], scale*vals[groups['40']][0], 0.0, 1.0, vals[groups['50']][0]*math.pi/180.0, vals[groups['51']][0]*math.pi/180.0)

def export_ELLIPSE():
    # mandatory group codes : (10, 11, 20, 21, 40, 41, 42) (xc, xm, yc, ym, width ratio, angle1, angle2)
    if vals[groups['10']] and vals[groups['11']] and vals[groups['20']] and vals[groups['21']] and vals[groups['40']] and vals[groups['41']] and vals[groups['42']]:
        generate_ellipse(vals[groups['10']][0], vals[groups['20']][0], scale*vals[groups['11']][0], scale*vals[groups['21']][0], vals[groups['40']][0], vals[groups['41']][0], vals[groups['42']][0])

def export_LEADER():
    # mandatory group codes : (10, 20) (x, y)
    if vals[groups['10']] and vals[groups['20']]:
        if len(vals[groups['10']]) > 1 and len(vals[groups['20']]) == len(vals[groups['10']]):
            path = 'M %f,%f' % (vals[groups['10']][0], vals[groups['20']][0])
            for i in range (1, len(vals[groups['10']])):
                path += ' %f,%f' % (vals[groups['10']][i], vals[groups['20']][i])
            attribs = {'d': path, 'style': style}
            inkex.etree.SubElement(layer, 'path', attribs)

def export_LWPOLYLINE():
    # mandatory group codes : (10, 20, 70) (x, y, flags)
    if vals[groups['10']] and vals[groups['20']] and vals[groups['70']]:
        if len(vals[groups['10']]) > 1 and len(vals[groups['20']]) == len(vals[groups['10']]):
            a=seqs
            if (seqs[-2]=='42' or seqs[-1]=='42') and vals[groups['70']][0]==1:
                if seqs[-1]=='42':
                    a=seqs
                    a.append("10")
                    a.append("20")
                else:
                    a=seqs[0:-1]
                    a.append("10")
                    a.append("20")
                    a.append(seqs[-1])
                vals[groups['10']].append(vals[groups['10']][0])
                vals[groups['20']].append(vals[groups['20']][0])
            # optional group codes : (42) (bulge)
            iseqs = 0
            ibulge = 0
            while a[iseqs] != '20':
                iseqs += 1
            path = 'M %f,%f' % (vals[groups['10']][0], vals[groups['20']][0])
            xold = vals[groups['10']][0]
            yold = vals[groups['20']][0]
            for i in range (1, len(vals[groups['10']])):
                bulge = 0
                iseqs += 1
                while a[iseqs] != '20':
                    if a[iseqs] == '42':
                        bulge = vals[groups['42']][ibulge]
                        ibulge += 1
                    iseqs += 1
                if bulge:
                    sweep = 0                   # sweep CCW
                    if bulge < 0:
                        sweep = 1               # sweep CW
                        bulge = -bulge
                    large = 0                   # large-arc-flag
                    if bulge > 1:
                        large = 1
                    r = math.sqrt((vals[groups['10']][i] - xold)**2 + (vals[groups['20']][i] - yold)**2)
                    r = 0.25*r*(bulge + 1.0/bulge)
                    path += ' A %f,%f 0.0 %d %d %f,%f' % (r, r, large, sweep, vals[groups['10']][i], vals[groups['20']][i])
                else:
                    path += ' L %f,%f' % (vals[groups['10']][i], vals[groups['20']][i])
                xold = vals[groups['10']][i]
                yold = vals[groups['20']][i]
            if vals[groups['70']][0] == 1:      # closed path
                path += ' z'
            attribs = {'d': path, 'style': style}
            inkex.etree.SubElement(layer, 'path', attribs)

def export_HATCH():
    # mandatory group codes : (10, 20, 70, 72, 92, 93) (x, y, fill, Edge Type, Path Type, Number of edges)
    if vals[groups['10']] and vals[groups['20']] and vals[groups['70']] and vals[groups['72']] and vals[groups['92']] and vals[groups['93']]:
        if vals[groups['70']][0] and len(vals[groups['10']]) > 1 and len(vals[groups['20']]) == len(vals[groups['10']]):
            # optional group codes : (11, 21, 40, 50, 51, 73) (x, y, r, angle1, angle2, CCW)
            i10 = 1    # count start points
            i11 = 0    # count line end points
            i40 = 0    # count circles
            i72 = 0    # count edge type flags
            path = ''
            for i in range (0, len(vals[groups['93']])):
                xc = vals[groups['10']][i10]
                yc = vals[groups['20']][i10]
                if vals[groups['72']][i72] == 2:            # arc
                    rm = scale*vals[groups['40']][i40]
                    a1 = vals[groups['50']][i40]
                    path += 'M %f,%f ' % (xc + rm*math.cos(a1*math.pi/180.0), yc + rm*math.sin(a1*math.pi/180.0))
                else:
                    a1 = 0
                    path += 'M %f,%f ' % (xc, yc)
                for j in range(0, vals[groups['93']][i]):
                    if vals[groups['92']][i] & 2:           # polyline
                        if j > 0:
                            path += 'L %f,%f ' % (vals[groups['10']][i10], vals[groups['20']][i10])
                        if j == vals[groups['93']][i] - 1:
                            i72 += 1
                    elif vals[groups['72']][i72] == 2:      # arc
                        xc = vals[groups['10']][i10]
                        yc = vals[groups['20']][i10]
                        rm = scale*vals[groups['40']][i40]
                        a2 = vals[groups['51']][i40]
                        diff = (a2 - a1 + 360) % (360)
                        sweep = 1 - vals[groups['73']][i40] # sweep CCW
                        large = 0                           # large-arc-flag
                        if diff:
                            path += 'A %f,%f 0.0 %d %d %f,%f ' % (rm, rm, large, sweep, xc + rm*math.cos(a2*math.pi/180.0), yc + rm*math.sin(a2*math.pi/180.0))
                        else:
                            path += 'A %f,%f 0.0 %d %d %f,%f ' % (rm, rm, large, sweep, xc + rm*math.cos((a1+180.0)*math.pi/180.0), yc + rm*math.sin((a1+180.0)*math.pi/180.0))
                            path += 'A %f,%f 0.0 %d %d %f,%f ' % (rm, rm, large, sweep, xc + rm*math.cos(a1*math.pi/180.0), yc + rm*math.sin(a1*math.pi/180.0))
                        i40 += 1
                        i72 += 1
                    elif vals[groups['72']][i72] == 1:      # line
                        path += 'L %f,%f ' % (scale*(vals[groups['11']][i11] - xmin), -scale*(vals[groups['21']][i11] - ymax))
                        i11 += 1
                        i72 += 1
                    i10 += 1
                path += "z "
            style = simplestyle.formatStyle({'fill': '%s' % color})
            attribs = {'d': path, 'style': style}
            inkex.etree.SubElement(layer, 'path', attribs)

def export_DIMENSION():
    # mandatory group codes : (10, 11, 13, 14, 20, 21, 23, 24) (x1..4, y1..4)
    if vals[groups['10']] and vals[groups['11']] and vals[groups['13']] and vals[groups['14']] and vals[groups['20']] and vals[groups['21']] and vals[groups['23']] and vals[groups['24']]:
        dx = abs(vals[groups['10']][0] - vals[groups['13']][0])
        dy = abs(vals[groups['20']][0] - vals[groups['23']][0])
        if (vals[groups['10']][0] == vals[groups['14']][0]) and dx > 0.00001:
            d = dx/scale
            dy = 0
            path = 'M %f,%f %f,%f' % (vals[groups['10']][0], vals[groups['20']][0], vals[groups['13']][0], vals[groups['20']][0])
        elif (vals[groups['20']][0] == vals[groups['24']][0]) and dy > 0.00001:
            d = dy/scale
            dx = 0
            path = 'M %f,%f %f,%f' % (vals[groups['10']][0], vals[groups['20']][0], vals[groups['10']][0], vals[groups['23']][0])
        else:
            return
        attribs = {'d': path, 'style': style + '; marker-start: url(#DistanceX); marker-end: url(#DistanceX)'}
        inkex.etree.SubElement(layer, 'path', attribs)
        x = scale*(vals[groups['11']][0] - xmin)
        y = - scale*(vals[groups['21']][0] - ymax)
        size = 12                   # default fontsize in px
        if vals[groups['3']]:
            if DIMTXT.has_key(vals[groups['3']][0]):
                size = scale*DIMTXT[vals[groups['3']][0]]
                if size < 2:
                    size = 2
        attribs = {'x': '%f' % x, 'y': '%f' % y, 'style': 'font-size: %.1fpx; fill: %s' % (size, color)}
        if dx == 0:
            attribs.update({'transform': 'rotate (%f %f %f)' % (-90, x, y)})
        node = inkex.etree.SubElement(layer, 'text', attribs)
        tspan = inkex.etree.SubElement(node , 'tspan', {inkex.addNS('role','sodipodi'): 'line'})
        tspan.text = str(float('%.2f' % d))

def export_INSERT():
    # mandatory group codes : (2, 10, 20) (block name, x, y)
    if vals[groups['2']] and vals[groups['10']] and vals[groups['20']]:
        x = vals[groups['10']][0]
        y = vals[groups['20']][0] - scale*ymax
        attribs = {'x': '%f' % x, 'y': '%f' % y, inkex.addNS('href','xlink'): '#' + quote(vals[groups['2']][0].encode("utf-8"))}
        inkex.etree.SubElement(layer, 'use', attribs)

def export_BLOCK():
    # mandatory group codes : (2) (block name)
    if vals[groups['2']]:
        global block
        block = inkex.etree.SubElement(defs, 'symbol', {'id': vals[groups['2']][0]})

def export_ENDBLK():
    global block
    block = defs                                    # initiallize with dummy

def export_ATTDEF():
    # mandatory group codes : (1, 2) (default, tag)
    if vals[groups['1']] and vals[groups['2']]:
        vals[groups['1']][0] = vals[groups['2']][0]
        export_MTEXT()

def generate_ellipse(xc, yc, xm, ym, w, a1, a2):
    rm = math.sqrt(xm*xm + ym*ym)
    a = math.atan2(ym, xm)
    diff = (a2 - a1 + 2*math.pi) % (2*math.pi)
    if abs(diff) > 0.0000001 and abs(diff - 2*math.pi) > 0.0000001: # open arc
        large = 0                   # large-arc-flag
        if diff > math.pi:
            large = 1
        xt = rm*math.cos(a1)
        yt = w*rm*math.sin(a1)
        x1 = xt*math.cos(a) - yt*math.sin(a)
        y1 = xt*math.sin(a) + yt*math.cos(a)
        xt = rm*math.cos(a2)
        yt = w*rm*math.sin(a2)
        x2 = xt*math.cos(a) - yt*math.sin(a)
        y2 = xt*math.sin(a) + yt*math.cos(a)
        path = 'M %f,%f A %f,%f %f %d 0 %f,%f' % (xc+x1, yc-y1, rm, w*rm, -180.0*a/math.pi, large, xc+x2, yc-y2)
    else:                           # closed arc
        path = 'M %f,%f A %f,%f %f 1 0 %f,%f %f,%f %f 1 0 %f,%f z' % (xc+xm, yc-ym, rm, w*rm, -180.0*a/math.pi, xc-xm, yc+ym, rm, w*rm, -180.0*a/math.pi, xc+xm, yc-ym)
    attribs = {'d': path, 'style': style}
    inkex.etree.SubElement(layer, 'path', attribs)

def generate_gcodetools_point(xc, yc):
		path=	'm %s,%s 2.9375,-6.343750000001 0.8125,1.90625 6.843748640396,-6.84374864039 0,0 0.6875,0.6875 -6.84375,6.84375 1.90625,0.812500000001 z' % (xc,yc)
		attribs = {'d': path, 'dxfpoint':'1', 'style': 'stroke:#ff0000;fill:#ff0000'}
		inkex.etree.SubElement(layer, 'path', attribs)

def get_line():
    return (stream.readline().strip(), stream.readline().strip())

def get_group(group):
    line = get_line()
    if line[0] == group:
        return float(line[1])
    else:
        return 0.0

#   define DXF Entities and specify which Group Codes to monitor

entities = {'MTEXT': export_MTEXT, 'TEXT': export_MTEXT, 'POINT': export_POINT, 'LINE': export_LINE, 'SPLINE': export_SPLINE, 'CIRCLE': export_CIRCLE, 'ARC': export_ARC, 'ELLIPSE': export_ELLIPSE, 'LEADER': export_LEADER, 'LWPOLYLINE': export_LWPOLYLINE, 'HATCH': export_HATCH, 'DIMENSION': export_DIMENSION, 'INSERT': export_INSERT, 'BLOCK': export_BLOCK, 'ENDBLK': export_ENDBLK, 'ATTDEF': export_ATTDEF, 'DICTIONARY': False}
groups = {'1': 0, '2': 1, '3': 2, '6': 3, '8': 4, '10': 5, '11': 6, '13': 7, '14': 8, '20': 9, '21': 10, '23': 11, '24': 12, '40': 13, '41': 14, '42': 15, '50': 16, '51': 17, '62': 18, '70': 19, '72': 20, '73': 21, '92': 22, '93': 23, '370': 24}
colors = {  1: '#FF0000',   2: '#FFFF00',   3: '#00FF00',   4: '#00FFFF',   5: '#0000FF',
            6: '#FF00FF',   8: '#414141',   9: '#808080',  12: '#BD0000',  30: '#FF7F00',
          250: '#333333', 251: '#505050', 252: '#696969', 253: '#828282', 254: '#BEBEBE', 255: '#FFFFFF'}

parser = inkex.optparse.OptionParser(usage="usage: %prog [options] SVGfile", option_class=inkex.InkOption)
parser.add_option("--auto", action="store", type="inkbool", dest="auto", default=True)
parser.add_option("--scale", action="store", type="string", dest="scale", default="1.0")
parser.add_option("--gcodetoolspoints", action="store", type="inkbool", dest="gcodetoolspoints", default=True)
parser.add_option("--encoding", action="store", type="string", dest="input_encode", default="latin_1")
parser.add_option("--tab", action="store", type="string", dest="tab", default="Options")
parser.add_option("--inputhelp", action="store", type="string", dest="inputhelp", default="")
(options, args) = parser.parse_args(inkex.sys.argv[1:])
doc = inkex.etree.parse(StringIO('<svg xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"></svg>'))
desc = inkex.etree.SubElement(doc.getroot(), 'desc', {})
defs = inkex.etree.SubElement(doc.getroot(), 'defs', {})
marker = inkex.etree.SubElement(defs, 'marker', {'id': 'DistanceX', 'orient': 'auto', 'refX': '0.0', 'refY': '0.0', 'style': 'overflow:visible'})
inkex.etree.SubElement(marker, 'path', {'d': 'M 3,-3 L -3,3 M 0,-5 L  0,5', 'style': 'stroke:#000000; stroke-width:0.5'})
stream = open(args[0], 'r')
xmax = xmin = 0.0
ymax = 297.0                                        # default A4 height in mm
line = get_line()
flag = 0                                            # (0, 1, 2, 3) = (none, LAYER, LTYPE, DIMTXT)
layer_colors = {}                                   # store colors by layer
layer_nodes = {}                                    # store nodes by layer
linetypes = {}                                      # store linetypes by name
DIMTXT = {}                                         # store DIMENSION text sizes

while line[0] and line[1] != 'BLOCKS':
    line = get_line()
    if options.auto:
        if line[1] == '$EXTMIN':
            xmin = get_group('10')
        if line[1] == '$EXTMAX':
            xmax = get_group('10')
            ymax = get_group('20')
    if flag == 1 and line[0] == '2':
        layername = unicode(line[1], options.input_encode)
        attribs = {inkex.addNS('groupmode','inkscape'): 'layer', inkex.addNS('label','inkscape'): '%s' % layername}
        layer_nodes[layername] = inkex.etree.SubElement(doc.getroot(), 'g', attribs)
    if flag == 2 and line[0] == '2':
        linename = unicode(line[1], options.input_encode)
        linetypes[linename] = []
    if flag == 3 and line[0] == '2':
        stylename = unicode(line[1], options.input_encode)
    if line[0] == '2' and line[1] == 'LAYER':
        flag = 1
    if line[0] == '2' and line[1] == 'LTYPE':
        flag = 2
    if line[0] == '2' and line[1] == 'DIMSTYLE':
        flag = 3
    if flag == 1 and line[0] == '62':
        layer_colors[layername] = int(line[1])
    if flag == 2 and line[0] == '49':
        linetypes[linename].append(float(line[1]))
    if flag == 3 and line[0] == '140':
        DIMTXT[stylename] = float(line[1])
    if line[0] == '0' and line[1] == 'ENDTAB':
        flag = 0

if options.auto:
    scale = 1.0
    if xmax > xmin:
        scale = 210.0/(xmax - xmin)                 # scale to A4 width
else:
    scale = float(options.scale)                    # manual scale factor
desc.text = '%s - scale = %f' % (unicode(args[0], options.input_encode), scale)
scale *= 90.0/25.4                                  # convert from mm to pixels

if not layer_nodes:
    attribs = {inkex.addNS('groupmode','inkscape'): 'layer', inkex.addNS('label','inkscape'): '0'}
    layer_nodes['0'] = inkex.etree.SubElement(doc.getroot(), 'g', attribs)
    layer_colors['0'] = 7

for linename in linetypes.keys():                   # scale the dashed lines
    linetype = ''
    for length in linetypes[linename]:
        linetype += '%.4f,' % math.fabs(length*scale)
    linetypes[linename] = 'stroke-dasharray:' + linetype

entity = ''
block = defs                                        # initiallize with dummy
while line[0] and line[1] != 'DICTIONARY':
    line = get_line()
    if entity and groups.has_key(line[0]):
        seqs.append(line[0])                        # list of group codes
        if line[0] == '1' or line[0] == '2' or line[0] == '3' or line[0] == '6' or line[0] == '8':  # text value
            val = line[1].replace('\~', ' ')
            val = inkex.re.sub( '\\\\A.*;', '', val)
            val = inkex.re.sub( '\\\\H.*;', '', val)
            val = inkex.re.sub( '\\^I', '', val)
            val = inkex.re.sub( '{\\\\L', '', val)
            val = inkex.re.sub( '}', '', val)
            val = inkex.re.sub( '\\\\S.*;', '', val)
            val = inkex.re.sub( '\\\\W.*;', '', val)
            val = unicode(val, options.input_encode)
            val = val.encode('unicode_escape')
            val = inkex.re.sub( '\\\\\\\\U\+([0-9A-Fa-f]{4})', '\\u\\1', val)
            val = val.decode('unicode_escape')
        elif line[0] == '62' or line[0] == '70' or line[0] == '92' or line[0] == '93':
            val = int(line[1])
        elif line[0] == '10' or line[0] == '13' or line[0] == '14': # scaled float x value
            val = scale*(float(line[1]) - xmin)
        elif line[0] == '20' or line[0] == '23' or line[0] == '24': # scaled float y value
            val = - scale*(float(line[1]) - ymax)
        else:                                       # unscaled float value
            val = float(line[1])
        vals[groups[line[0]]].append(val)
    elif entities.has_key(line[1]):
        if entities.has_key(entity):
            if block != defs:                       # in a BLOCK
                layer = block
            elif vals[groups['8']]:                 # use Common Layer Name
                layer = layer_nodes[vals[groups['8']][0]]
            color = '#000000'                       # default color
            if vals[groups['8']]:
                if layer_colors.has_key(vals[groups['8']][0]):
                    if colors.has_key(layer_colors[vals[groups['8']][0]]):
                        color = colors[layer_colors[vals[groups['8']][0]]]
            if vals[groups['62']]:                  # Common Color Number
                if colors.has_key(vals[groups['62']][0]):
                    color = colors[vals[groups['62']][0]]
            style = simplestyle.formatStyle({'stroke': '%s' % color, 'fill': 'none'})
            w = 0.5                                 # default lineweight for POINT
            if vals[groups['370']]:                 # Common Lineweight
                if vals[groups['370']][0] > 0:
                    w = 90.0/25.4*vals[groups['370']][0]/00.0
                    if w < 0.5:
                        w = 0.5
                    style = simplestyle.formatStyle({'stroke': '%s' % color, 'fill': 'none', 'stroke-width': '%.1f' % w})
            if vals[groups['6']]:                   # Common Linetype
                if linetypes.has_key(vals[groups['6']][0]):
                    style += ';' + linetypes[vals[groups['6']][0]]
            entities[entity]()
        entity = line[1]
        vals = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        seqs = []

doc.write(inkex.sys.stdout)

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
