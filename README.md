# Seam carving

## Introduction
The code in this repository allows to resize an image using [seam carving](http://graphics.cs.cmu.edu/courses/15-463/2007_fall/hw/proj2/imret.pdf) algorithm.

## Algorithm outline with step-by-step images

1. While the image is not in the desired size:
  1. Calculate the energies of the image pixels
  2. Find the lowest energy seam
  2. Add/remove seam

## Examples

### Scaling down
![animation resize to smaller](https://github.com/4gn3s/seam-carving/raw/master/static/smaller.gif)
### Scaling up
![animation resize to bigger](https://github.com/4gn3s/seam-carving/raw/master/static/bigger.gif)

## Todo
* better seam insertion algorithm (to prevent inserting the same seam again and again)
