#!/usr/bin/env python
import svgwrite
import math
import random
import colorsys

FIG_SIZE		= (1600,800)
SAMPLE_AREA		= (300,100,1000,600)
BKG_COLOR		= 'white'
PATH_STROKE		= 'black'
ICON_FILL		= 'black'
ICON_SIZE		= (15,15)
PATH_WDT		= 4
ICON_SIZE_RNG	= (10,20)
SAMPLES			= 30
TEMP_RANGES		= (15,20)
SALT_RANGES		= (29,32)
NOISE			= 0.05

LEGEND_STPS		= 6
LEGEND_PADDING	= 20
LEGEND_SIZE		= (180,2*(2+LEGEND_STPS)*(ICON_SIZE_RNG[1] + LEGEND_PADDING))
LEGEND_POS		= [(LEGEND_PADDING,100), (FIG_SIZE[0]-LEGEND_SIZE[0]-LEGEND_PADDING,100)]
DIR				= 'svg/'

# Text
FONT_SIZE		= 24
FONT_FAMILY		= 'sans-serif'
DESCRIPTION		= {'temp': 'Temp. (C)','sal': 'Salinity (PSU)'}

MODES			= [['size'], ['shape'], ['color'], ['color','size'], ['color','shape']]

meas = []
for t in range(SAMPLES):
	idx = float(t)/SAMPLES
	y = math.sin(4*math.pi*idx)
	px = SAMPLE_AREA[0] + idx*SAMPLE_AREA[2]
	py = SAMPLE_AREA[1] + 0.5*SAMPLE_AREA[3] + 0.5*y*SAMPLE_AREA[3]
	t = TEMP_RANGES[0] + (TEMP_RANGES[1]-TEMP_RANGES[0])*((0+idx)+random.uniform(-NOISE,+NOISE))
	s = SALT_RANGES[0] + (SALT_RANGES[1]-SALT_RANGES[0])*((1-idx)+random.uniform(-NOISE,+NOISE))
	meas.append({'loc': (px,py), 'temp': t, 'sal': s})

varbls = [['temp'], ['temp','sal']]

min_max = (1e9,-1e9)
lims = {
	'temp': min_max,
	'sal': min_max,
	}
for m in meas:
	for l in lims:
		lmin = lims[l][0]
		lmax = lims[l][1]
		if m[l] > lims[l][1]:
			lmax = m[l]
		if m[l] < lims[l][0]:
			lmin = m[l]
		lims[l] = (lmin,lmax,lmax-lmin)

def resize(lim, val):
	s = ICON_SIZE_RNG[1]*(val-lim[0])/lim[2] + ICON_SIZE_RNG[0]
	return (s,s)

def reshape(lim, val):
	a = (val-lim[0])/lim[2]
	b = 1-a
	a = ICON_SIZE_RNG[1]*a + ICON_SIZE_RNG[0]
	b = ICON_SIZE_RNG[1]*b + ICON_SIZE_RNG[0]
	return (a,b)

def recolor(lim, val):
	c = colorsys.hsv_to_rgb(0.5*(1+(val-lim[0])/lim[2]),1.0,1.0)
	RNG = 255
	c = (RNG*c[0],RNG*c[1],RNG*c[2])
	return "rgb(%d,%d,%d)" % c

def get_symbol(lim, val, mode, c=ICON_FILL, s=ICON_SIZE):
	if 'size' in mode:
		s = resize(lim,val)
	if 'shape' in mode:
		s = reshape(lim,val)
	if 'color' in mode:
		c = recolor(lim,val)
	return c,s

def draw_legend(var, mode, dwg, legend_pos, c, s):

	dwg.add(dwg.rect(insert=legend_pos, size=LEGEND_SIZE, fill=BKG_COLOR, stroke=PATH_STROKE))

	# Legend Title
	ltitle_x = legend_pos[0]+0.5*LEGEND_SIZE[0]
	ltitle_y = legend_pos[1]+FONT_SIZE+LEGEND_PADDING
	dwg.add(dwg.text(DESCRIPTION[var], insert=(ltitle_x,ltitle_y), font_size=FONT_SIZE, font_family=FONT_FAMILY, text_anchor='middle'))

	for i,m in enumerate(reversed([lims[var][0] + (lims[var][1]-lims[var][0])*float(k)/LEGEND_STPS for k in range(LEGEND_STPS+1)])):
		c,s = get_symbol(lims[var],m,mode,c,s)
		pix = legend_pos[0]+LEGEND_PADDING+ICON_SIZE_RNG[1]
		piy = legend_pos[1]+LEGEND_PADDING+2*(1+i)*(ICON_SIZE_RNG[1] + LEGEND_PADDING)
		ptx = pix+LEGEND_PADDING+ICON_SIZE_RNG[1]
		pty = piy+0.5*FONT_SIZE
		dwg.add(dwg.ellipse(center=(pix,piy), r=s, fill=c))
		dwg.add(dwg.text('%9.3f'%m, insert=(ptx,pty), font_size=FONT_SIZE, font_family=FONT_FAMILY, text_anchor='start'))

for var in varbls:
	print var
	for mode in MODES:
		if len(var) <= len(mode):
			print '\t',mode

			# Init canvas
			filename = DIR+'-'.join(var)+'-'+'-'.join(mode)+'.svg'
			dwg = svgwrite.Drawing(filename, size=FIG_SIZE)
			dwg.add(dwg.rect(size=FIG_SIZE, fill=BKG_COLOR, stroke='none'))

			# Arrow
			marker = dwg.marker(insert=(0,3), size=(10,10), orient='auto')
			marker.add(dwg.path(d="M0,0 L0,6 L9,3 z", fill=PATH_STROKE))
			dwg.defs.add(marker)

			# Path
			p = meas[0]
			for m in meas:
				line = dwg.add(dwg.line(start=p['loc'],end=m['loc'], stroke=PATH_STROKE, stroke_width=PATH_WDT))
				if m == meas[-1]:
					line['marker-end'] = marker.get_funciri()
				p = m

			# Measurements
			for m in meas[:-1]:
				for i,v in enumerate(var):
					if len(var) == 1:
						md = mode
					else:
						md = mode[i]
					if v == var[0]:
						c,s = get_symbol(lims[v],m[v],md)
					else:
						c,s = get_symbol(lims[v],m[v],md,c,s)
					draw_legend(v, md, dwg, LEGEND_POS[i], c, s)
				dwg.add(dwg.ellipse(center=m['loc'], r=s, fill=c))

			dwg.save()