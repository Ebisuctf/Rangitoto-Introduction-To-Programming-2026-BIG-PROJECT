import random


class Star:
    """
    Single parallax star in the background.

    Args:
        pos (tuple[float, float]): Starting world position.
        img (pygame.Surface): Star image.
        speed (float): Horizontal movement speed.
        depth (float): Parallax depth multiplier.

    Bounty difficulty: ⭐⭐☆☆☆ (2/5)

    Developed by: ______________________________
    """
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        """
        Move the star horizontally at its configured speed.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        self.pos[0] += self.speed

    def _parallax_position(self, offset):
        """
        Compute parallax-adjusted position based on camera offset and depth.

        Args:
            offset (tuple[int, int]): Camera offset.

        Returns:
            tuple[float, float]: Adjusted x, y for rendering.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        return (
            self.pos[0] - offset[0] * self.depth,
            self.pos[1] - offset[1] * self.depth,
        )

    def render(self, surf, offset=(0, 0)):
        """
        Draw the star image with wrapping so it reappears on the opposite side.

        Args:
            surf (pygame.Surface): Surface to draw on.
            offset (tuple[int, int]): Camera offset.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        render_x, render_y = self._parallax_position(offset)
        w, h = surf.get_width(), surf.get_height()
        iw, ih = self.img.get_width(), self.img.get_height()
        surf.blit(
            self.img,
            (
                render_x % (w + iw) - iw,
                render_y % (h + ih) - ih,
            ),
        )


class Stars:
    """
    Manages a collection of parallax stars.

    Args:
        star_images (list[pygame.Surface]): Available star images to choose from.
        count (int): Number of stars to spawn.

    Bounty difficulty: ⭐⭐☆☆☆ (2/5)

    Developed by: ______________________________
    """
    def __init__(self, star_images, count=16):
        self.stars = []
        self._spawn_initial_stars(star_images, count)
        self._sort_by_depth()

    def _spawn_initial_stars(self, star_images, count):
        """
        Create the initial set of stars with random positions and depths.

        Args:
            star_images (list[pygame.Surface]): Images to choose from.
            count (int): Number of stars to create.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        for _ in range(count):
            pos = (random.random() * 99999, random.random() * 99999)
            img = random.choice(star_images)
            speed = random.random() * 0.05 + 0.05
            depth = random.random() * 0.06 + 0.2
            self.stars.append(Star(pos, img, speed, depth))

    def _sort_by_depth(self):
        """
        Sort stars so closer ones are rendered last.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        self.stars.sort(key=lambda star: star.depth)

    def update(self):
        """
        Update all managed stars.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        for star in self.stars:
            star.update()

    def render(self, surf, offset=(0, 0)):
        """
        Render all stars with the given camera offset.

        Args:
            surf (pygame.Surface): Surface to draw on.
            offset (tuple[int, int]): Camera offset.

        Returns:
            None.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        for star in self.stars:
            star.render(surf, offset=offset)
