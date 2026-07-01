import pygame
import os

BASE_IMG_PATH = "data/images/"


def load_image(path):
    """
    Load a single image from the BASE_IMG_PATH folder.

    Args:
        path (str): Relative path inside the images folder, e.g. 'player/idle/0.png'.

    Returns:
        pygame.Surface: The loaded image surface with black treated as transparent.

    Bounty difficulty: ⭐☆☆☆☆ (1/5)

    Developed by: ______________________________
    """
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img


def load_images(path):
    """
    Load all images from a folder inside BASE_IMG_PATH.

    Args:
        path (str): Relative folder path inside the images folder, e.g. 'player/idle'.

    Returns:
        list[pygame.Surface]: A list of loaded image surfaces sorted by filename.

    Bounty difficulty: ⭐⭐☆☆☆ (2/5)

    Developed by: ______________________________
    """
    images = []
    folder = BASE_IMG_PATH + path
    for img_name in sorted(os.listdir(folder)):
        images.append(load_image(path + '/' + img_name))
    return images


class Animation:
    """
    Basic animation class that cycles through a list of images over time.

    Args:
        images (list[pygame.Surface]): Frames of the animation.
        img_dur (int): How many game frames each image should be displayed.
        loop (bool): Whether the animation should loop once it reaches the end.

    Attributes:
        images (list[pygame.Surface]): Stored animation frames.
        loop (bool): Looping flag.
        img_duration (int): Per-frame display duration.
        done (bool): True when a non-looping animation reaches its final frame.
        frame (int): Current animation frame counter.

    Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

    Developed by: ______________________________
    """
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        """
        Create an independent copy of this Animation.

        Args:
            None.

        Returns:
            Animation: A new Animation instance with the same images and settings.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        """
        Advance the animation by one frame.

        Args:
            None.

        Returns:
            None. Updates frame counter and sets done when a non-looping animation finishes.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            max_frame = self.img_duration * len(self.images) - 1
            self.frame = min(self.frame + 1, max_frame)
            if self.frame >= max_frame:
                self.done = True

    def img(self):
        """
        Get the current image for this animation.

        Args:
            None.

        Returns:
            pygame.Surface: Current frame image based on frame counter.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        index = int(self.frame / self.img_duration)
        return self.images[index]
