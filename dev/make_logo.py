"""
The kwimage draw methods are powered by kwplot, so we are using this library to
make its own logo.
"""
import kwplot
import kwimage
import numpy as np
plt = kwplot.autoplt()
kwplot.autompl()

lhs = kwimage.draw_text_on_image(None, 'kw', color='kitware_blue')
rhs = kwimage.draw_text_on_image(None, 'plot', color='kitware_green')
poly1 = kwimage.Mask.coerce((lhs.sum(axis=2) > 0).astype(np.uint8)).to_multi_polygon()
poly2 = kwimage.Mask.coerce((rhs.sum(axis=2) > 0).astype(np.uint8)).to_multi_polygon()

poly1 = poly1.simplify(1)
poly2 = poly2.simplify(1)

poly2 = poly2.translate((0, poly1.to_box().br_y))

box1 = poly1.to_box().to_polygon()
box2 = poly2.to_box().to_polygon()

kwplot.figure(fnum=1, doclf=1, title='kwplot logo')

box1.union(box2).to_box().scale(1.1, about='center').draw(fill=False, facecolor=None, setlim=1)

poly1.draw(color='kitware_blue')
poly2.draw(color='kitware_green')

ax = plt.gca()
ax.invert_yaxis()
ax.set_aspect('equal')

fig = plt.gcf()
img = kwplot.render_figure_to_image(fig)
kwimage.imwrite('kwplot_logo.png', img)
