import pygame
import sys

from scripts.utils import load_images
from scripts.titlemap import Tilemap

RENDER_SCALE = 2.0


class Editor:
    """
    Simple tile-based level editor for the game.

    Args:
        None.

    Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

    Developed by: ______________________________
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        self.assets = self._load_editor_assets()
        self.movement = [False, False, False, False]
        pygame.display.set_caption("editor")
        self.tilemap = Tilemap(self, tile_size=16)
        self._try_load_default_map("map.json")
        self.scroll = [0, 0]
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

    def _load_editor_assets(self):
        """
        Load tile images for the editor palette.

        Args:
            None.

        Returns:
            dict: Mapping tile category names to lists of images.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        return {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "spawners": load_images("tiles/spawners"),
        }

    def _try_load_default_map(self, path):
        """
        Attempt to load a tilemap from the given path, ignoring missing files.

        Args:
            path (str): Map filename.

        Returns:
            None.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        try:
            self.tilemap.load(path)
        except FileNotFoundError:
            pass

    def _update_camera_scroll(self):
        """
        Update the editor camera based on movement keys.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
        self.scroll[1] += (self.movement[3] - self.movement[2]) * 2

    def _get_mouse_tile_position(self):
        """
        Convert mouse position to tile coordinates under the current camera.

        Args:
            None.

        Returns:
            tuple[int, int]: Tile grid position.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        mpos = pygame.mouse.get_pos()
        mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
        tile_x = int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size)
        tile_y = int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size)
        return tile_x, tile_y, mpos

    def _get_current_tile_image(self):
        """
        Fetch the currently selected tile image.

        Args:
            None.

        Returns:
            pygame.Surface: Copy of the selected tile image with alpha set.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
        img.set_alpha(100)
        return img

    def _place_or_remove_tiles(self, tile_pos, mpos):
        """
        Handle placing and removing tiles based on mouse state.

        Args:
            tile_pos (tuple[int, int]): Current tile grid position.
            mpos (tuple[float, float]): Mouse position in scaled coordinates.

        Returns:
            None.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        if self.clicking and self.ongrid:
            key = f"{tile_pos[0]};{tile_pos[1]}"
            self.tilemap.tilemap[key] = {
                "type": self.tile_list[self.tile_group],
                "variant": self.tile_variant,
                "pos": tile_pos,
            }
        if self.right_clicking:
            key = f"{tile_pos[0]};{tile_pos[1]}"
            if key in self.tilemap.tilemap:
                del self.tilemap.tilemap[key]
            for tile in self.tilemap.offgrid_tiles.copy():
                tile_img = self.assets[tile["type"]][tile["variant"]]
                tile_r = pygame.Rect(
                    tile["pos"][0] - self.scroll[0],
                    tile["pos"][1] - self.scroll[1],
                    tile_img.get_width(),
                    tile_img.get_height(),
                )
                if tile_r.collidepoint(mpos):
                    self.tilemap.offgrid_tiles.remove(tile)

    def _handle_mouse_event(self, event, mpos):
        """
        Process mouse down/up events for clicking, right-clicking and scrolling.

        Args:
            event (pygame.event.Event): Mouse event.
            mpos (tuple[float, float]): Mouse position in editor coordinates.

        Returns:
            None.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.clicking = True
                if not self.ongrid:
                    self.tilemap.offgrid_tiles.append(
                        {
                            "type": self.tile_list[self.tile_group],
                            "variant": self.tile_variant,
                            "pos": (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1]),
                        }
                    )
            if event.button == 3:
                self.right_clicking = True
            if self.shift:
                if event.button == 4:
                    self.tile_variant = (self.tile_variant - 1) % len(
                        self.assets[self.tile_list[self.tile_group]]
                    )
                if event.button == 5:
                    self.tile_variant = (self.tile_variant + 1) % len(
                        self.assets[self.tile_list[self.tile_group]]
                    )
            else:
                if event.button == 4:
                    self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                    self.tile_variant = 0
                if event.button == 5:
                    self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                    self.tile_variant = 0
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.clicking = False
            if event.button == 3:
                self.right_clicking = False

    def _handle_key_event(self, event):
        """
        Process keyboard events for camera movement and editor commands.

        Args:
            event (pygame.event.Event): Key event.

        Returns:
            None.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.movement[0] = True
            if event.key == pygame.K_d:
                self.movement[1] = True
            if event.key == pygame.K_w:
                self.movement[2] = True
            if event.key == pygame.K_s:
                self.movement[3] = True
            if event.key == pygame.K_g:
                self.ongrid = not self.ongrid
            if event.key == pygame.K_t:
                self.tilemap.autotile()
            if event.key == pygame.K_o:
                self.tilemap.save("map.json")
            if event.key == pygame.K_LSHIFT:
                self.shift = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.movement[0] = False
            if event.key == pygame.K_d:
                self.movement[1] = False
            if event.key == pygame.K_w:
                self.movement[2] = False
            if event.key == pygame.K_s:
                self.movement[3] = False
            if event.key == pygame.K_LSHIFT:
                self.shift = False

    def run(self):
        """
        Main editor loop. Handles camera, tile placement and rendering.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        while True:
            self.display.fill((0, 0, 0))
            self._update_camera_scroll()
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.tilemap.render(self.display, offset=render_scroll)
            tile_x, tile_y, mpos = self._get_mouse_tile_position()
            current_tile_img = self._get_current_tile_image()

            if self.ongrid:
                self.display.blit(
                    current_tile_img,
                    (
                        tile_x * self.tilemap.tile_size - self.scroll[0],
                        tile_y * self.tilemap.tile_size - self.scroll[1],
                    ),
                )
            else:
                self.display.blit(current_tile_img, mpos)

            self._place_or_remove_tiles((tile_x, tile_y), mpos)
            self.display.blit(current_tile_img, (5, 5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._handle_mouse_event(event, mpos)
                self._handle_key_event(event)

            self.screen.blit(
                pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)
            )
            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    Editor().run()
