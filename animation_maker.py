import numpy as np
import scipy.misc
from moviepy.editor import ImageSequenceClip


class AnimationMaker:
    def __init__(self):
        self.sequence = []
        self.max_width = 0
        self.max_height = 0
        self.max_dimensions= 0
        self.default_FPS = 25

    def add(self, image):
        self.sequence.append(image)
        if self.max_height < image.height:
            self.max_height = image.height
        if self.max_width < image.width:
            self.max_width = image.width
        if self.max_dimensions < image.dim:
            self.max_dimensions = image.dim

    @property
    def clip(self):
        new_sequence = []
        for i, image in enumerate(self.sequence):
            image_array = image.array
            resized = np.zeros((self.max_height, self.max_width, self.max_dimensions))
            resized[:image_array.shape[0], :image_array.shape[1], :image_array.shape[2]] = image_array
            new_sequence.append(resized)
        return ImageSequenceClip(new_sequence, fps=self.default_FPS)

    def export_webm(self, filename="debug/animation.webm"):
        self.clip.write_videofile(filename, audio=False)

    def export_gif(self, filename="debug/animation.gif"):
        self.clip.write_gif(filename, fps=self.default_FPS)
