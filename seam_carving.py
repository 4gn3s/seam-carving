import numpy as np
import scipy.misc
import scipy.ndimage

from image import Image
from animation_maker import AnimationMaker

IMAGE_FILE = 'image.jpg'


class SeamCarver:
    def __init__(self, image_file):
        self.image = Image.from_file(image_file)
        self.debug_animation = AnimationMaker()

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
        return Image.from_image_array(array=seam_image)

    def cut_seam(self):
        seam = self.seam()
        result = np.zeros((self.image.height, self.image.width - 1, self.image.dim))
        print(seam.array.shape)
        for i in range(0, self.image.dim):
            for j in range(0, self.image.height):
                result[j, :, i] = np.append(self.image.array[j, 0: seam.array[j, 0], i],
                                            self.image.array[j, seam.array[j, 0] + 1: self.image.width, i]
                                            )
        debug_image = self.image.debug(seam.array)
        self.debug_animation.add(Image.from_image_array(debug_image, transposed=seam.transposed))
        scipy.misc.imsave("debug/debug.jpg", debug_image)

        return Image.from_image_array(array=result, transposed=seam.transposed)

    def add_seam(self):
        seam = self.seam()
        result = np.zeros((self.image.height, self.image.width + 1, self.image.dim))
        for i in range(0, self.image.dim):
            for j in range(0, self.image.height):
                x = seam[j, 0]
                if x < self.image.width - 2:
                    vector_average = np.array([(self.image.array[j, x, i] + self.image.array[j, x + 1, i])/2.0])
                else:
                    vector_average = np.array([(self.image.array[j, x, i] + self.image.array[j, x - 1, i])/2.0])
                tmp = np.append(self.image.image[j, 0: seam[j, 0] + 1, i],
                                vector_average)
                result[j, :, i] = np.append(tmp, self.image.array[j, seam[j, 0] + 1: self.image.width, i])
        debug_image = self.image.debug(seam)
        scipy.misc.imsave("debug/debug.jpg", debug_image)

        return Image.from_image_array(array=result, transposed=seam.transposed)

    def cut_seams(self, desired_width):
        iterations = self.image.width - desired_width
        current_iteration = 0
        while current_iteration < iterations:
            print("Resizing from %s to %s" % (self.image.width, self.image.width-1))
            self.image = self.cut_seam()
            current_iteration += 1

    def resize(self, desired_width, desired_height):
        # this function should perform adding/ removing seams as needed
        self.cut_seams(desired_width)
        self.image.do_transpose()
        self.cut_seams(desired_height)
        return self.image

if __name__ == '__main__':
    # create gif showing each steps
    sc = SeamCarver(IMAGE_FILE)
    # for x in range(100):
    #     sc.image = Image().from_image(sc.add_seam())
    image = sc.resize(400, 400)
    # scipy.misc.imsave("final.jpg", sc.image)
    sc.debug_animation.export_gif()
