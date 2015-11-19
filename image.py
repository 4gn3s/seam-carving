import numpy as np
import scipy.misc
import scipy.ndimage


class Image:
    def __init__(self, array=None, transposed=False):
        self.array = array
        self.width = 0
        self.height = 0
        self.dim = 0
        self.initialize()
        self.greyscale_coeffs = [.299, .587, .144]
        self.transposed = transposed
        if transposed:
            self.do_transpose()
        self.greyscale_image = None
        self.sobel_image = None
        self.min_energy_image = None

    def do_transpose(self):
        if self.dim == 3:
            self.array = self.array.transpose(1, 0, 2)
        else:
            self.array = self.array.transpose(1, 0)
        self.transposed = not self.transposed
        self.initialize()
        return self.array

    @classmethod
    def from_image(cls, image):
        return cls(image.array, image.transposed)

    @classmethod
    def from_image_array(cls, array, transposed=False):
        return cls(array, transposed)

    @classmethod
    def from_file(cls, image_file):
        return cls(scipy.misc.imread(image_file))

    def initialize(self):
        self.width = self.array.shape[1]
        self.height = self.array.shape[0]
        if len(self.array.shape) > 2:
            self.dim = self.array.shape[2]

    @property
    def greyscale(self):
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
        # add an argument to save file to a directory
        image = self.array.copy()
        color = [255] * 3
        for i in range(len(seam)):
            image[i][seam[i][0]] = color
        if self.transposed:
            image = image.transpose(1, 0, 2)
        return image
