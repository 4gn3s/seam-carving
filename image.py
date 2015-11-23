import numpy as np
import scipy.misc
import scipy.ndimage
from PIL import Image as PILImage


class Image:
    def __init__(self, array=None, transposed=False):
        self._array = array
        self.greyscale_coeffs = [.299, .587, .144]
        self.transposed = transposed
        self.greyscale_image = None
        self.sobel_image = None
        self.min_energy_image = None

    @property
    def array(self):
        """
        :return: the image array (transposed if needed)
        """
        if self.transposed:
            if self.dim == 3:
                return self._array.transpose(1, 0, 2)
            else:
                return self._array.transpose(1, 0)
        return self._array

    @property
    def width(self):
        if self.transposed:
            return self._array.shape[0]
        return self._array.shape[1]

    @property
    def height(self):
        if self.transposed:
            return self._array.shape[1]
        return self._array.shape[0]

    @property
    def dim(self):
        if len(self._array.shape) > 2:
            return self._array.shape[2]
        return 2

    @classmethod
    def from_image(cls, image):
        return cls(image.array, image.transposed)

    @classmethod
    def from_image_array(cls, array, transposed=False):
        return cls(array, transposed)

    @classmethod
    def from_file(cls, image_file):
        return cls(scipy.misc.imread(image_file))

    @property
    def greyscale(self):
        """
        :return: greyscale image transposed if needed
        """
        if not self.greyscale_image:
            self.greyscale_image = np.dot(self.array[:, :, :3], self.greyscale_coeffs)
        return self.greyscale_image

    @property
    def energy(self):
        """
        Based on http://stackoverflow.com/questions/7185655/applying-the-sobel-filter-using-scipy#1
        """
        if not self.sobel_image:
            greyscale = self.greyscale.astype('int32')
            dx = scipy.ndimage.sobel(greyscale, 0)  # horizontal derivative
            dy = scipy.ndimage.sobel(greyscale, 1)  # vertical derivative
            self.sobel_image = np.hypot(dx, dy)  # magnitude
            self.sobel_image *= 255.0 / np.max(self.sobel_image)  # normalize
        return self.sobel_image
    
    @property
    def min_energy(self):
        """
        Converts energy values to cumulative energy values
        """
        if not self.min_energy_image:
            image = self.energy
            self.min_energy_image = np.zeros((self.height, self.width))
            self.min_energy_image[0][:] = image[0][:]

            for i in range(self.height):
                for j in range(self.width):
                    if i == 0:
                        self.min_energy_image[i, j] = image[i, j]
                    elif j == 0:
                        self.min_energy_image[i, j] = image[i, j] + min(
                            self.min_energy_image[i - 1, j],
                            self.min_energy_image[i - 1, j + 1]
                        )
                    elif j == self.width - 1:
                        self.min_energy_image[i, j] = image[i, j] + min(
                            self.min_energy_image[i - 1, j - 1],
                            self.min_energy_image[i - 1, j]
                        )
                    else:
                        self.min_energy_image[i, j] = image[i, j] + min(
                            self.min_energy_image[i - 1, j - 1],
                            self.min_energy_image[i - 1, j],
                            self.min_energy_image[i - 1, j + 1]
                        )
        return self.min_energy_image

    def debug(self, seam):
        """
        :param seam: current seam in the image (2 dim array with one column/row)
        :return: a debug image showing the actual image being processed with the currently chosen seam
        """
        image = self.array
        color = [255] * 3
        seam_array = seam.array
        size = seam.width if seam.width > seam.height else seam.height
        for i in range(size):
            if seam.transposed:
                image[i][seam_array[0][i]] = color
            else:
                image[i][seam_array[i][0]] = color
        return image

    def save(self, filename):
        im = PILImage.fromarray(self.array.astype('uint8'))
        im.save(filename)
