import numpy as np

from image import Image
from animation_maker import AnimationMaker


class SeamCarver:
    def __init__(self, image_file):
        self.image = Image.from_file(image_file)
        self.debug_animation = AnimationMaker()

    def seams(self, n):
        """
        Finds the n minimum seams in the image
        :param n: the number of paths to be found
        :return a list of Image objects, each containing the a path, sorted ascending
        """
        image = self.image.min_energy
        seams_found = []
        for iteration in range(n):
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
                image[i, j] = float("Inf")
            seams_found.append(Image.from_image_array(array=seam_image, transposed=self.image.transposed))
        return seams_found

    def cut_seam(self):
        seam = self.seams(1)[0]
        result = np.zeros((self.image.height, self.image.width - 1, self.image.dim))
        for i in range(0, self.image.dim):
            for j in range(0, self.image.height):
                if seam.transposed:
                    result[j, :, i] = np.append(self.image.array[j, 0: seam.array[0, j], i],
                                                self.image.array[j, seam.array[0, j] + 1: self.image.width, i]
                                                )
                else:
                    result[j, :, i] = np.append(self.image.array[j, 0: seam.array[j, 0], i],
                                                self.image.array[j, seam.array[j, 0] + 1: self.image.width, i]
                                                )
        debug_image = self.image.debug(seam)
        self.debug_animation.add(Image.from_image_array(debug_image, transposed=self.image.transposed))

        if self.image.transposed:
            result = result.transpose(1, 0, 2)

        return Image.from_image_array(array=result, transposed=self.image.transposed)

    def add_seam(self, seam):
        result = np.zeros((self.image.height, self.image.width + 1, self.image.dim))
        for i in range(0, self.image.dim):
            for j in range(0, self.image.height):
                x = seam.array[0, j] if seam.transposed else seam.array[j, 0]
                if x < self.image.width - 2:
                    vector_average = np.array([(self.image.array[j, x, i] + self.image.array[j, x + 1, i])/2.0])
                else:
                    vector_average = np.array([(self.image.array[j, x, i] + self.image.array[j, x - 1, i])/2.0])

                tmp = np.append(self.image.array[j, 0: x + 1, i], vector_average)
                result[j, :, i] = np.append(tmp, self.image.array[j, x + 1: self.image.width, i])

        debug_image = self.image.debug(seam)
        self.debug_animation.add(Image.from_image_array(debug_image, transposed=self.image.transposed))

        if self.image.transposed:
            result = result.transpose(1, 0, 2)

        return Image.from_image_array(array=result, transposed=seam.transposed)

    def cut_seams(self, desired_width):
        iterations = self.image.width - desired_width
        current_iteration = 0
        while current_iteration < iterations:
            print("Resizing from %s to %s" % (self.image.width, self.image.width-1))
            self.image = self.cut_seam()
            current_iteration += 1

    def add_seams(self, desired_width):
        iterations = desired_width - self.image.width
        seams = self.seams(iterations)
        current_iteration = 0
        while current_iteration < iterations:
            print("Resizing from %s to %s" % (self.image.width, self.image.width+1))
            self.image = self.add_seam(seams[current_iteration])
            current_iteration += 1

    def resize(self, desired_width, desired_height):
        if desired_width < self.image.width:
            self.cut_seams(desired_width)
        else:
            self.add_seams(desired_width)

        if desired_height < self.image.height:
            self.image.transposed = True
            self.cut_seams(desired_height)
            self.image.transposed = False
        else:
            self.image.transposed = True
            self.add_seams(desired_height)
            self.image.transposed = False

        return self.image
