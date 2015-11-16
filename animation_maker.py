from moviepy.editor import ImageSequenceClip

class AnimationMaker:
    def __init__(self):
        self.sequence = []
        self.max_width = 0
        self.max_height = 0
        self.max_dimensions= 0
        self.default_FPS = 25

    def add(self, image):
        self.sequence.append(image.image)
        if self.max_height < image.height:
            self.max_height = image.height
        if self.max_width < image.width:
            self.max_width = image.width
        if self.max_dimensions < image.dim:
            self.max_dimensions = image.dim

    @property
    def clip(self):
        # resize all images in the sequence here
        for image in self.sequence:
            image.resize((self.max_height, self.max_width, self.max_dimensions))
        return ImageSequenceClip(self.sequence, fps=self.default_FPS)

    def export_webm(self, filename="animation.webm"):
        self.clip.write_videofile(filename, audio=False)

    def export_gif(self, filename="animation.gif"):
        self.clip.write_gif(filename, fps=self.default_FPS)
