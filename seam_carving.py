import numpy as np
import scipy.misc
import scipy.ndimage

IMAGE_FILE = 'image.jpg'

class SeamCarver:
    def __init__(self, image):
        self.image = scipy.misc.imread(image)
        self.initialize()

    def initialize(self):
        self.width = self.image.shape[1]
        self.height = self.image.shape[0]
        self.dim = self.image.shape[2]
        self.grayscale_image = None

    @property
    def grayscale(self):
        if not self.grayscale_image:
            self.grayscale_image = np.dot(self.image[:, :, :3], [.299, .587, .144])
        return self.grayscale_image

    def energy(self):
        """
        Based on http://stackoverflow.com/questions/7185655/applying-the-sobel-filter-using-scipy#1
        """
        grayscale = self.grayscale.astype('int32')
        dx = scipy.ndimage.sobel(grayscale, 0)  # horizontal derivative
        dy = scipy.ndimage.sobel(grayscale, 1)  # vertical derivative
        sobel_image = np.hypot(dx, dy)  # magnitude
        sobel_image *= 255.0 / np.max(sobel_image)  # normalize
        return sobel_image

    def min_energy(self):
        """
        Converts energy values to cumulative energy values
        """
        image = self.energy()
        out_image = np.zeros((self.height, self.width))
        out_image[0][:] = image[0][:]

        for i in range(self.height):
            for j in range(self.width):
                if i == 0:
                    out_image[i, j] = image[i, j]
                elif j == 0:
                    out_image[i, j] = image[i, j] + min(out_image[i - 1, j], out_image[i - 1, j + 1])
                elif j == self.width - 1:
                    out_image[i, j] = image[i, j] + min(out_image[i - 1, j - 1], out_image[i - 1, j])
                else:
                    out_image[i, j] = image[i, j] + min(out_image[i - 1, j - 1], out_image[i - 1, j], out_image[i - 1, j + 1])
        return out_image

    def seam(self):
        """
        Finds the shortest path
        """
        image = self.min_energy()
        seam_image = np.zeros((self.height, 1))
        i = self.height - 1
        # start: minimum enery in the bottom row
        min_value = min(image[i,:])
        j = np.where(image[i][:] == min_value)[0][0]
        i -= 1
        while i >= -1:
            if seam_image[i + 1, 0] == 0:
                t = [float("Inf"), image[i, seam_image[i + 1, 0]], image[i, seam_image[i + 1, 0] + 1]]
            elif seam_image[i + 1, 0] == self.width - 1:
                t = [image[i, seam_image[i + 1, 0] - 1], image[i, seam_image[i + 1, 0]], float("Inf")]
            else:
                t = [image[i, seam_image[i + 1, 0] - 1], image[i, seam_image[i + 1, 0]], image[i, seam_image[i + 1, 0] + 1]]
            j = seam_image[i + 1, 0] + np.argmin(t) - 1
            seam_image[i, 0] = j
            i -= 1
        return seam_image

    def cut_seam(self):
        seam = self.seam()
        result = np.zeros((self.height, self.width - 1, self.dim))
        for i in range(0, self.dim):
            for j in range(0, self.height):
                if seam[j, 0] ==  0:
                    result[j, :, i] = self.image[j, 1 : self.width, i]
                elif seam[j, 0] == self.width - 1:
                    result[j, :, i] = self.image[j, 0 : self.width - 1, i]
                else:
                    result[j, :, i] = np.append(self.image[j, 0 : seam[j, 0], i],
                                              self.image[j, seam[j, 0] + 1 : self.width,i])
        debug_image = self.debug(seam)
        scipy.misc.imsave("debug.jpg", debug_image)

        return result

    def debug(self, seam):
        image = self.image.copy()
        color = [255] * 3
        for i in range(len(seam)):
            image[i][seam[i][0]] = color
        return image

    def cut_seams(self, desired_width):
        iterations = self.width - desired_width + 1
        current_iteration = 0
        while current_iteration < iterations:
            print("Resizing from %s to %s", self.width, self.width-1)
            self.image = self.cut_seam()
            self.initialize()
            current_iteration += 1
        return self.image

    def resize(self, desired_width, desired_height):
        image = self.cut_seams(desired_width)
        #maybe this trick does not work so well
        self.image = image.transpose(1, 0, 2)
        self.initialize()
        image = self.cut_seams(desired_height)
        image = image.transpose(1, 0, 2)
        return image

if __name__ == '__main__':
    sc = SeamCarver(IMAGE_FILE)
    image = sc.resize(400, 200)
    scipy.misc.imsave("final.jpg", image)
