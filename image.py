import numpy as np
import scipy.misc
import scipy.ndimage


class Image:
    def __init__(self):
        self.greyscale_coeffs = [.299, .587, .144]
        self.transposed = False
        self.image = None
        self.width = 0
        self.height = 0
        self.dim = 0
        self.greyscale_image = None
        self.sobel_image = None
        self.min_energy_image = None

    def transpose(self):
        self.image = self.image.transpose(1, 0, 2)
        self.transposed = not self.transposed
        return self.image

    def from_image(self, image):
        self.image = image
        self.initialize()
        return self

    def from_file(self, image_file):
        self.image = scipy.misc.imread(image_file)
        self.initialize()
        return self

    def initialize(self):
        self.width = self.image.shape[1]
        self.height = self.image.shape[0]
        self.dim = self.image.shape[2]
        self.greyscale_image = None

    @property
    def greyscale(self):
        if not self.greyscale_image:
            self.greyscale_image = np.dot(self.image[:, :, :3], self.greyscale_coeffs)
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
        image = self.image.copy()
        color = [255] * 3
        for i in range(len(seam)):
            image[i][seam[i][0]] = color
        if self.transposed:
            image = image.transpose(1, 0, 2)
        return image
