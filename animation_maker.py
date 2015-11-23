import numpy as np
import moviepy.editor as mpy


class AnimationMaker:
    """
    Makes an animation out of a sequence of Images
    """
    def __init__(self):
        self.sequence = []
        self.max_width = 0
        self.max_height = 0
        self.max_dimensions = 0
        self.default_FPS = 25
        self.current_step = 0

    def add(self, image):
        self.sequence.append(image)
        if self.max_height < image.height:
            self.max_height = image.height
        if self.max_width < image.width:
            self.max_width = image.width
        if self.max_dimensions < image.dim:
            self.max_dimensions = image.dim

    def frame(self, t):
        image = self.sequence[self.current_step]
        self.current_step += 1
        image_array = image.array
        resized = np.zeros((self.max_height, self.max_width, self.max_dimensions))
        resized.fill(255)  # to have gifs with white background
        shape = image_array.shape
        resized[:shape[0], :shape[1], :shape[2]] = image_array
        return resized

    @property
    def clip(self):
        self.current_step = 0
        return mpy.VideoClip(self.frame, duration=(len(self.sequence)-1)/self.default_FPS)

    def export_webm(self, filename="debug/animation.webm"):
        self.clip.write_videofile(filename, audio=False)

    def export_gif(self, filename="debug/animation.gif"):
        self.clip.write_gif(filename, fps=self.default_FPS)
