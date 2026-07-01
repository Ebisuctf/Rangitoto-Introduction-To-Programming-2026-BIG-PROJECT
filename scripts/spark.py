import math
import pygame


class Spark:
    """
    Simple spark effect with a diamond-shaped polygon.

    Args:
        pos (tuple[float, float]): Starting world position.
        angle (float): Direction angle in radians.
        speed (float): Initial speed of the spark.

    Bounty difficulty: ⭐⭐☆☆☆ (2/5)

    Developed by: ______________________________
    """
    def __init__(self, pos, angle, speed):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed

    def update(self):
        """
        Move the spark forward and reduce its speed over time.

        Args:
            None.

        Returns:
            bool: True if the spark should be removed (speed reached zero).

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed
        self.speed = max(0, self.speed - 0.1)
        return not self.speed

    def _build_polygon_points(self, offset):
        """
        Compute the list of points forming the spark polygon.

        Args:
            offset (tuple[int, int]): Camera offset for rendering.

        Returns:
            list[tuple[float, float]]: Four points describing the diamond.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        ox, oy = offset
        main_dx = math.cos(self.angle) * self.speed * 3
        main_dy = math.sin(self.angle) * self.speed * 3
        side1_dx = math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5
        side1_dy = math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5
        side2_dx = math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5
        side2_dy = math.sin(self.angle - math.pi * 0.5) * self.speed * 0.5

        return [
            (self.pos[0] + main_dx - ox, self.pos[1] + main_dy - oy),
            (self.pos[0] + side1_dx - ox, self.pos[1] + side1_dy - oy),
            (self.pos[0] - main_dx - ox, self.pos[1] - main_dy - oy),
            (self.pos[0] + side2_dx - ox, self.pos[1] + side2_dy - oy),
        ]

    def render(self, surf, offset=(0, 0)):
        """
        Render the spark polygon on the given surface.

        Args:
            surf (pygame.Surface): Surface to draw on.
            offset (tuple[int, int]): Camera offset for rendering.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        points = self._build_polygon_points(offset)
        pygame.draw.polygon(surf, (255, 255, 255), points)
