import pygame
import json

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

NEIGHBOR_OFFSETS = [
    (-1, 0), (-1, -1), (0, -1), (1, -1),
    (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1),
]
PHYSICS_TILES = {"grass", "stone"}
AUTOTILE_TYPES = {"grass", "stone"}


class Tilemap:
    """
    Stores and renders a tile-based level layout.

    Args:
        game: Game or Editor instance that provides assets.
        tile_size (int): Size of each tile in pixels.

    Bounty difficulty: ⭐⭐☆☆☆ (2/5)

    Developed by: ______________________________
    """
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def extract(self, id_pairs, keep=False):
        """
        Find tiles matching any (type, variant) pair.

        Args:
            id_pairs (list[tuple[str, int]]): Tile (type, variant) pairs to match.
            keep (bool): If False, remove matched tiles from tilemap and offgrid.

        Returns:
            list[dict]: Copies of matching tile dictionaries with pixel positions.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in list(self.tilemap.keys()):
            tile = self.tilemap[loc]
            if (tile["type"], tile["variant"]) in id_pairs:
                copy_tile = tile.copy()
                copy_tile["pos"] = copy_tile["pos"].copy()
                copy_tile["pos"][0] *= self.tile_size
                copy_tile["pos"][1] *= self.tile_size
                matches.append(copy_tile)
                if not keep:
                    del self.tilemap[loc]
        return matches

    def tiles_around(self, pos):
        """
        Get all tiles around a pixel position based on NEIGHBOR_OFFSETS.

        Args:
            pos (tuple[float, float]): Pixel position.

        Returns:
            list[dict]: Tiles around the position.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = f"{tile_loc[0] + offset[0]};{tile_loc[1] + offset[1]}"
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    def save(self, path):
        """
        Save tilemap data to a JSON file.

        Args:
            path (str): Output file path.

        Returns:
            None.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        with open(path, "w") as f:
            json.dump(
                {
                    "tilemap": self.tilemap,
                    "tile_size": self.tile_size,
                    "offgrid": self.offgrid_tiles,
                },
                f,
            )

    def load(self, path):
        """
        Load tilemap data from a JSON file.

        Args:
            path (str): Input file path.

        Returns:
            None. Sets tilemap, tile_size and offgrid_tiles.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        with open(path, "r") as f:
            map_data = json.load(f)
        self.tilemap = map_data["tilemap"]
        self.tile_size = map_data["tile_size"]
        self.offgrid_tiles = map_data["offgrid"]

    def solid_check(self, pos):
        """
        Check whether a physics-enabled tile exists at the given pixel position.

        Args:
            pos (tuple[float, float]): Pixel position.

        Returns:
            dict | None: Tile dictionary if solid tile exists, otherwise None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        tile_loc = f"{int(pos[0] // self.tile_size)};{int(pos[1] // self.tile_size)}"
        if tile_loc in self.tilemap:
            tile = self.tilemap[tile_loc]
            if tile["type"] in PHYSICS_TILES:
                return tile
        return None

    def physics_rect_around(self, pos):
        """
        Build collision rectangles for physics tiles around a pixel position.

        Args:
            pos (tuple[float, float]): Pixel position.

        Returns:
            list[pygame.Rect]: Rectangles representing solid tiles.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        rects = []
        for tile in self.tiles_around(pos):
            if tile["type"] in PHYSICS_TILES:
                rects.append(
                    pygame.Rect(
                        tile["pos"][0] * self.tile_size,
                        tile["pos"][1] * self.tile_size,
                        self.tile_size,
                        self.tile_size,
                    )
                )
        return rects

    def autotile(self):
        """
        Automatically choose tile variants based on neighboring tiles.

        Args:
            None.

        Returns:
            None. Mutates tilemap variants in place.

        Bounty difficulty: ⭐⭐⭐⭐☆ (4/5)

        Developed by: ______________________________
        """
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = f"{tile['pos'][0] + shift[0]};{tile['pos'][1] + shift[1]}"
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]["type"] == tile["type"]:
                        neighbors.add(shift)
            neighbors_key = tuple(sorted(neighbors))
            if tile["type"] in AUTOTILE_TYPES and neighbors_key in AUTOTILE_MAP:
                tile["variant"] = AUTOTILE_MAP[neighbors_key]

    def render(self, surf, offset=(0, 0)):
        """
        Render off-grid and grid tiles to the target surface.

        Args:
            surf (pygame.Surface): Target surface.
            offset (tuple[int, int]): Camera offset.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        # Off-grid tiles first (background decor)
        for tile in self.offgrid_tiles:
            img = self.game.assets[tile["type"]][tile["variant"]]
            surf.blit(img, (tile["pos"][0] - offset[0], tile["pos"][1] - offset[1]))

        # Grid-aligned tiles
        start_x = offset[0] // self.tile_size
        end_x = (offset[0] + surf.get_width()) // self.tile_size + 1
        start_y = offset[1] // self.tile_size
        end_y = (offset[1] + surf.get_height()) // self.tile_size + 1

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                loc = f"{x};{y}"
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    img = self.game.assets[tile["type"]][tile["variant"]]
                    surf.blit(
                        img,
                        (
                            tile["pos"][0] * self.tile_size - offset[0],
                            tile["pos"][1] * self.tile_size - offset[1],
                        ),
                    )
