class Particles:
    """
    Represents a single on-screen particle with position, velocity and animation.

    Args:
        game: The Game instance providing assets and configuration.
        p_type (str): Particle type key, e.g. 'leaf' or 'particle'.
        pos (tuple[float, float]): Starting world position of the particle.
        velocity (list[float, float]): Initial velocity in x and y directions.
        frame (int): Starting frame index for the particle animation.

    Bounty difficulty: ⭐⭐☆☆☆ (2/5)

    Developed by: ______________________________
    """
    def __init__(self, game, p_type, pos, velocity=None, frame=0):
        if velocity is None:
            velocity = [0, 0]
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self._create_animation(frame)

    def _create_animation(self, frame):
        """
        Create and configure the Animation object used by this particle.

        Args:
            frame (int): Initial animation frame index.

        Returns:
            Animation: Copied animation from game assets with frame set.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        animation = self.game.assets['particle/' + self.type].copy()
        animation.frame = frame
        return animation

    def update(self):
        """
        Update particle position and animation state.

        Args:
            None.

        Returns:
            bool: True if the particle should be removed (its animation is done).

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        kill = False
        if self.animation.done:
            kill = True

        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.animation.update()
        return kill

    def render(self, surf, offset=(0, 0)):
        """
        Draw the particle's current frame to the provided surface.

        Args:
            surf (pygame.Surface): Surface to draw on.
            offset (tuple[int, int]): Camera offset to subtract from world position.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        img = self.animation.img()
        x = self.pos[0] - offset[0] - img.get_width() // 2
        y = self.pos[1] - offset[1] - img.get_height() // 2
        surf.blit(img, (x, y))
