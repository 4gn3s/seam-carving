# Seam carving

## Introduction
The code in this repository allows to resize an image using [seam carving](http://graphics.cs.cmu.edu/courses/15-463/2007_fall/hw/proj2/imret.pdf) algorithm.

## Algorithm outline

1. While the image is not in the desired size:
  1. Calculate the energies of the image pixels
  2. Find the lowest energy seam
  2. Add/remove seam
  
## A detailed description of the algorithm
Seam carving algorithm is used to perform content aware resizing of images.

#### Energy
The algorithm can be used to either enlarge or reduce the size of an image, using areas that contain less information for the viewer.
The information is the image is defined using energy of each pixel. 
TODO SOBEL DESCRIPTION
TODO ENERGY IMAGE

#### Seams
The process of adding or removing pixels in the image cannot be performed at random. Addition or removal of pixels in the image at random positions would create a distorted image. If we add or remove whole rows or columns with minimal energy, artifacts might arise in the picture.
The solution is to use seams- paths in the image, which traverse it horizontally/vertically in such way, that for each pixel (i,j) in the seam, the next pixel has to be one of the following:

  1. Vertical seam:
    * *(i+1, j-1)*
    * *(i+1, j)*
    * *(i+1, j+1)*
  2. Horizontal seam:
    * *(i-1, j+1)*
    * *(i, j+1)*
    * *(i+1, j+1)*
   
The goal is to find a seam with minimal energy values.
To find a seam with minimal energy, we can use dynamic programming:

  1. create new image *M*
  2. fill the first row with energy values *e*
  3. for all other rows, fill pixels using the formula: 
*M[i, j] = e[i, j] + min(M[i-1, j], M[i, j], M[i+1, j])*
  4. find the minimum value in the last row and traverse back, choosing pixels with lowest *M* values.
 
### Removal/ insertion of the seam
To decrease the size of an image, a simple iterative procedure can be performed:

  1. Find a seam
  2. Remove it 

Adding new seams is a more tricky part. Insertion of new seams can be thought of as performing seam removal in reverse. If we need to insert *n* seams, then we need to find *n* different seams for removal and add them to the image.

## Examples

### Scaling down
![animation resize to smaller](https://github.com/4gn3s/seam-carving/raw/master/static/smaller.gif)

### Scaling up
![animation resize to bigger](https://github.com/4gn3s/seam-carving/raw/master/static/bigger.gif)

## Todo
* algorithm choosing the currently optimal horizontal/vertical seam to remove (as described [here](http://kirilllykov.github.io/blog/2013/06/06/seam-carving-algorithm/))
* use [forward energy](http://cs.brown.edu/courses/cs129/results/proj3/taox/) in seam removal
* add mask processing to allow object removal (mask defines an area with energy equal to zero)
* seam carving for videos: add another dimension time *t*

## Interesting resources:

* [http://www.cs.cmu.edu/afs/andrew/scs/cs/15-463/f07/proj2/www/wwedler/](http://www.cs.cmu.edu/afs/andrew/scs/cs/15-463/f07/proj2/www/wwedler/)
* [http://jeremykun.com/2013/03/04/seam-carving-for-content-aware-image-scaling/](http://jeremykun.com/2013/03/04/seam-carving-for-content-aware-image-scaling/)
