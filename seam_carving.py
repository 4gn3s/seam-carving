import numpy as np
import scipy.misc
import scipy.ndimage

IMAGE_FILE = 'image.jpg'


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

    def from_image(self, image):
        self.image = image
        self.initialize()
        return self

    def from_file(self, image_file):
        self.image = scipy.misc.imread(image)
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
            self.greyscale_image = np.dot(self.image[:, :, :3], self.grayscale_coeffs)
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


class SeamCarver:
    def __init__(self, image_file):
        self.image = Image().from_file(image_file)

    def seam(self):
        """
        Finds the shortest path
        """
        image = self.image.min_energy
        seam_image = np.zeros((self.image.height, 1))
        for i in reversed(range(0, self.image.height)):
            if i == self.image.height - 1:
                value = min(image[i, :])
                j = np.where(image[i][:] == value)[0][0]
            else:
                if seam_image[i + 1, 0] == 0:
                    tmp = [
                        float("Inf"),
                        image[i, seam_image[i + 1, 0]],
                        image[i, seam_image[i + 1, 0] + 1]
                    ]
                elif seam_image[i + 1, 0] == self.image.width - 1:
                    tmp = [
                        image[i, seam_image[i + 1, 0] - 1],
                        image[i, seam_image[i + 1, 0]],
                        float("Inf")
                    ]
                else:
                    tmp = [
                        image[i, seam_image[i + 1, 0] - 1],
                        image[i, seam_image[i + 1, 0]],
                        image[i, seam_image[i + 1, 0] + 1]
                    ]
                j = seam_image[i+1, 0] + np.argmin(tmp) - 1
            seam_image[i, 0] = j
        return seam_image

    def cut_seam(self):
        seam = self.seam()
        result = np.zeros((self.image.height, self.image.width - 1, self.image.dim))
        for i in range(0, self.image.dim):
            for j in range(0, self.image.height):
                result[j, :, i] = np.append(self.image.image[j, 0: seam[j, 0], i],
                                            self.image.image[j, seam[j, 0] + 1: self.image.width, i]
                                            )
        debug_image = self.debug(seam)
        scipy.misc.imsave("debug.jpg", debug_image)

        return result

    def add_seam(self):
        seam = self.seam()
        result = np.zeros((self.image.height, self.image.width + 1, self.image.dim))
        for i in range(0, self.image.dim):
            for j in range(0, self.image.height):
                result[j, :, i] = np.append(self.image.image[j, 0: seam[j, 0] + 1, i],
                                            # we should take the average of neighbouring two columns
                                            self.image.image[j, seam[j, 0]: self.image.width, i]
                                            )
        debug_image = self.debug(seam)
        scipy.misc.imsave("debug.jpg", debug_image)

        return result

    def cut_seams(self, desired_width):
        iterations = self.image.width - desired_width + 1
        current_iteration = 0
        while current_iteration < iterations:
            print("Resizing from %s to %s" % (self.image.width, self.image.width-1))
            self.image = Image().from_image(self.cut_seam())
            current_iteration += 1
        return self.image

    def resize(self, desired_width, desired_height):
        # this function should perform adding/ removing seams as needed
        image = self.cut_seams(desired_width)
        self.image = Image().from_image(image.transpose(1, 0, 2))
        image = self.cut_seams(desired_height)
        image = image.transpose(1, 0, 2)
        return image

if __name__ == '__main__':
    # think of creating an ipython notebook to show each steps
    # create gif showing each steps
    sc = SeamCarver(IMAGE_FILE)
    for x in xrange(100):
        sc.image = Image().from_image(sc.add_seam())
        sc.initialize()
    #image = sc.resize(400, 200)
    scipy.misc.imsave("final.jpg", sc.image)
