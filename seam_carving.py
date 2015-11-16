import numpy as np
import scipy.misc
import scipy.ndimage

from image import Image

IMAGE_FILE = 'image.jpg'


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
        debug_image = self.image.debug(seam)
        scipy.misc.imsave("debug.jpg", debug_image)

        return result

    def add_seam(self):
        seam = self.seam()
        result = np.zeros((self.image.height, self.image.width + 1, self.image.dim))
        for i in range(0, self.image.dim):
            for j in range(0, self.image.height):
                x = seam[j, 0]
                if x < self.image.width - 2:
                    vector_average = np.array([(self.image.image[j, x, i] + self.image.image[j, x + 1, i])/2.0])
                else:
                    vector_average = np.array([(self.image.image[j, x, i] + self.image.image[j, x - 1, i])/2.0])
                tmp = np.append(self.image.image[j, 0: seam[j, 0] + 1, i],
                                vector_average)
                result[j, :, i] = np.append(tmp, self.image.image[j, seam[j, 0] + 1: self.image.width, i])
        debug_image = self.image.debug(seam)
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
        self.image = Image().from_image(image.transpose())
        image = self.cut_seams(desired_height)
        image = image.transpose()
        return image

if __name__ == '__main__':
    # think of creating an ipython notebook to show each steps
    # create gif showing each steps
    sc = SeamCarver(IMAGE_FILE)
    for x in xrange(100):
        sc.image = Image().from_image(sc.add_seam())
    # image = sc.resize(300, 200)
    scipy.misc.imsave("final.jpg", sc.image)
