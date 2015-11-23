from seam_carving import SeamCarver


IMAGE_FILE = 'static/image.jpg'


def scale_down_example():
    sc = SeamCarver(IMAGE_FILE)
    image = sc.resize(200, 300)
    image.save("static/smaller.jpg")
    sc.debug_animation.export_gif("static/smaller.gif")


def scale_up_example():
    sc = SeamCarver(IMAGE_FILE)
    image = sc.resize(500, 500)
    image.save("static/bigger.jpg")
    sc.debug_animation.export_gif("static/bigger.gif")


if __name__ == '__main__':
    scale_down_example()
    scale_up_example()
