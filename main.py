import pygame
import sys
import random
import math
import os

from scripts.utils import load_image, load_images, Animation
from scripts.entities import Player, Enemy
from scripts.titlemap import Tilemap
from scripts.stars import Stars
from scripts.particle import Particles
from scripts.spark import Spark

vmusic = random.randint(1, 2)


class Game:
    """
    Core game class that manages the main loop, entities, camera, particles,
    transitions and input handling.

    Args:
        None.

    Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

    Developed by: ______________________________
    """
    def __init__(self):
        """
        Initialize the game window, rendering surfaces, clock, assets,
        sounds, player and tilemap.

        Args:
            None.

        Returns:
            None. Sets attributes such as screen, display, assets,
            tilemap, player, enemies, particles and sounds.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.assets = self._load_assets()
        self.sfx = self._load_sounds()
        self._configure_sound_volumes()
        self.stars = Stars(self.assets["stars"], count=16)
        pygame.display.set_caption("ChosenOne")
        self.player = Player(self, (50, 50), (8, 15))
        self.tilemap = Tilemap(self, tile_size=16)
        self.level = 0
        self.load_level(self.level)
        self.screenshake = 0

    def _load_assets(self):
        """
        Load image assets and animations for tiles, entities, background
        and particles.

        Args:
            None.

        Returns:
            dict: Mapping asset keys to pygame.Surface or Animation objects.

        Dependencies:
            - load_image(path)
            - load_images(path)
            - Animation(images)

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        return {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "background": load_image("locations/blue.jpg"),
            "stars": load_images("tiles/star"),
            "enemy/idle": Animation(load_images("enemy/idle"), img_dur=6),
            "enemy/run": Animation(load_images("enemy/run"), img_dur=4),
            "player/idle": Animation(load_images("player/idle"), img_dur=6),
            "player/run": Animation(load_images("player/run"), img_dur=4),
            "player/jump": Animation(load_images("player/jump")),
            "player/slide": Animation(load_images("player/slide")),
            "player/wall_slide": Animation(load_images("player/wall_slide")),
            "particle/leaf": Animation(load_images("particles/leaf"), img_dur=20, loop=False),
            "particle/particle": Animation(load_images("particles/particle"), img_dur=6, loop=False),
            "gun": load_image("gun.png"),
            "projectile": load_image("projectile.png"),
        }

    def _load_sounds(self):
        """
        Load sound effects used in the game.

        Args:
            None.

        Returns:
            dict: Mapping names like 'jump', 'shoot' to Sound objects.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        return {
            "jump": pygame.mixer.Sound("data/sfx/jump.wav"),
            "shoot": pygame.mixer.Sound("data/sfx/shoot.wav"),
            "hit": pygame.mixer.Sound("data/sfx/hit.wav"),
            "dash": pygame.mixer.Sound("data/sfx/dash.wav"),
            "ambience": pygame.mixer.Sound("data/sfx/ambience.wav"),
        }

    def _configure_sound_volumes(self):
        """
        Set default volume levels for sound effects.

        Args:
            None.

        Returns:
            None. Adjusts volume on sounds in self.sfx.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        self.sfx["ambience"].set_volume(0.4)
        self.sfx["dash"].set_volume(0.3)
        self.sfx["hit"].set_volume(0.8)
        self.sfx["shoot"].set_volume(0.4)
        self.sfx["jump"].set_volume(0.7)

    def load_level(self, map_id):
        """
        Load the given level, set up leaf spawners, enemies, projectiles,
        particles, and camera / transition state.

        Args:
            map_id (int): Identifier of the map JSON file in data/maps.

        Returns:
            None.

        Dependencies:
            - Tilemap.load(path)
            - Tilemap.extract(id_pairs, keep)
            - Enemy(game, pos, size)
            - Player.pos, Player.air_time

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        self.tilemap.load(f"data/maps/{map_id}.json")
        self.leaf_spawners = []
        for tree in self.tilemap.extract([("large_decor", 2)], keep=True):
            rect = pygame.Rect(4 + tree["pos"][0], 4 + tree["pos"][1], 23, 13)
            self.leaf_spawners.append(rect)
        self.enemies = []
        for spawner in self.tilemap.extract([("spawners", 0), ("spawners", 1)]):
            if spawner["variant"] == 0:
                self.player.pos = spawner["pos"]
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner["pos"], (8, 15)))
        self.projectiles = []
        self.particles = []
        self.sparks = []
        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30

    def _start_music(self):
        """
        Begin looping background music and ambience.

        Args:
            None.

        Returns:
            None. Uses global vmusic to select a track.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        if vmusic == 1:
            pygame.mixer.music.load("data/music/LittleStreetC.mp3")
        else:
            pygame.mixer.music.load("data/music/Beachy.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.4)
        self.sfx["ambience"].play(-1)

    def update_transition_state(self):
        """
        Update level-complete and death transitions.

        Args:
            None.

        Returns:
            None. Mutates self.transition, self.level and self.dead.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        if not len(self.enemies):
            self.transition += 1
            if self.transition > 30:
                self.level = min(self.level + 1, len(os.listdir("data/maps")) - 1)
                self.load_level(self.level)
        if self.transition < 0:
            self.transition += 1
        if self.dead:
            self.dead += 1
            if self.dead >= 10:
                self.transition = min(30, self.transition + 1)
            if self.dead > 40:
                self.load_level(self.level)

    def update_camera_scroll(self):
        """
        Smoothly move the camera scroll towards the player position.

        Args:
            None.

        Returns:
            None. Mutates self.scroll.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        target_x = self.player.rect().centerx - self.display.get_width() / 2
        target_y = self.player.rect().centery - self.display.get_height() / 2
        self.scroll[0] += int((target_x - self.scroll[0]) / 30)
        self.scroll[1] += int((target_y - self.scroll[1]) / 30)

    def spawn_leaf_particles(self):
        """
        Randomly spawn leaf particles from configured leaf spawner rectangles.

        Args:
            None.

        Returns:
            None. Appends Particles instances to self.particles.

        Bounty difficulty: ⭐⭐⭐⭐☆ (4/5)

        Developed by: ______________________________
        """
        for rect in self.leaf_spawners:
            if random.random() * 49999 < rect.width * rect.height:
                pos = (
                    rect.x + random.random() * rect.width,
                    rect.y + random.random() * rect.height,
                )
                self.particles.append(
                    Particles(
                        self,
                        "leaf",
                        pos,
                        velocity=[-0.1, 0.3],
                        frame=random.randint(0, 20),
                    )
                )

    def update_enemies(self, render_scroll):
        """
        Update and render all enemies, removing any that signal they are dead.

        Args:
            render_scroll (tuple[int, int]): Camera offset for rendering.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        for enemy in self.enemies.copy():
            kill = enemy.update(self.tilemap, (0, 0))
            enemy.render(self.display, offset=render_scroll)
            if kill:
                self.enemies.remove(enemy)

    def update_player(self, render_scroll):
        """
        Update and render the player if they are alive.

        Args:
            render_scroll (tuple[int, int]): Camera offset.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        if not self.dead:
            dx = self.movement[1] - self.movement[0]
            self.player.update(self.tilemap, (dx, 0))
            self.player.render(self.display, offset=render_scroll)

    def update_projectiles(self, render_scroll):
        """
        Move, render and manage projectiles including collisions and effects.

        Args:
            render_scroll (tuple[int, int]): Camera offset.

        Returns:
            None. Mutates projectiles, sparks, particles, dead and screenshake.

        Bounty difficulty: ⭐⭐⭐⭐☆ (4/5)

        Developed by: ______________________________
        """
        for projectile in self.projectiles.copy():
            projectile[0][0] += projectile[1]
            projectile[2] += 1
            img = self.assets["projectile"]
            self.display.blit(
                img,
                (
                    projectile[0][0] - img.get_width() / 2 - render_scroll[0],
                    projectile[0][1] - img.get_height() / 2 - render_scroll[1],
                ),
            )
            if self.tilemap.solid_check(projectile[0]):
                self.projectiles.remove(projectile)
                for _ in range(4):
                    angle = random.random() - 0.5 + (
                        math.pi if projectile[1] > 0 else 0
                    )
                    speed = 2 + random.random()
                    self.sparks.append(Spark(projectile[0], angle, speed))
            elif projectile[2] > 360:
                self.projectiles.remove(projectile)
            elif abs(self.player.dashing) < 50:
                if self.player.rect().collidepoint(projectile[0]):
                    self.projectiles.remove(projectile)
                    self.dead += 1
                    self.sfx["hit"].play()
                    self.screenshake = max(16, self.screenshake)
                    for _ in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.sparks.append(
                            Spark(
                                self.player.rect().center,
                                angle,
                                2 + random.random(),
                            )
                        )
                        self.particles.append(
                            Particles(
                                self,
                                "particle",
                                self.player.rect().center,
                                velocity=[
                                    math.cos(angle + math.pi) * speed * 0.5,
                                    math.sin(angle + math.pi) * speed * 0.5,
                                ],
                                frame=random.randint(0, 7),
                            )
                        )

    def update_sparks(self, render_scroll):
        """
        Update and render spark effects, removing finished sparks.

        Args:
            render_scroll (tuple[int, int]): Camera offset.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(self.display, offset=render_scroll)
            if kill:
                self.sparks.remove(spark)

    def apply_display_mask(self):
        """
        Apply a silhouette mask to the gameplay display to create a glow.

        Args:
            None.

        Returns:
            None. Blits silhouette multiple times to display_2.

        Bounty difficulty: ⭐⭐⭐⭐☆ (4/5)

        Developed by: ______________________________
        """
        display_mask = pygame.mask.from_surface(self.display)
        display_silhouette = display_mask.to_surface(
            setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0)
        )
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            self.display_2.blit(display_silhouette, offset)

    def update_particles(self, render_scroll):
        """
        Update and render all particles, including leaf sway motion.

        Args:
            render_scroll (tuple[int, int]): Camera offset.

        Returns:
            None. Mutates self.particles.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        for particle in self.particles.copy():
            kill = particle.update()
            if particle.type == "leaf":
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
            particle.render(self.display, offset=render_scroll)
            if kill:
                self.particles.remove(particle)

    def handle_input(self):
        """
        Handle window events and keyboard input for movement, jump and dash.

        Args:
            None.

        Returns:
            None. Mutates self.movement and calls Player.jump/dash.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: Amit Sahaf - 197821
        """
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.movement[0] = True
                if event.key == pygame.K_RIGHT:
                    self.movement[1] = True
                if event.key == pygame.K_UP:
                    if self.player.jump():
                        self.sfx["jump"].play()
                if event.key == pygame.K_x:
                    self.player.dash()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.movement[0] = False
                if event.key == pygame.K_RIGHT:
                    self.movement[1] = False

    def draw_transition_circle(self):
        """
        Draw the white transition circle effect over the gameplay display.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        if self.transition:
            transition_surf = pygame.Surface(self.display.get_size())
            pygame.draw.circle(
                transition_surf,
                (255, 255, 255),
                (self.display.get_width() // 2, self.display.get_height() // 2),
                (30 - abs(self.transition)) * 8,
            )
            transition_surf.set_colorkey((255, 255, 255))
            self.display.blit(transition_surf, (0, 0))

    def present_frame(self):
        """
        Combine the gameplay display with the background, apply screenshake
        and present the frame to the main window.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        self.display_2.blit(self.display, (0, 0))
        screenshake_offset = (
            random.random() * self.screenshake - self.screenshake / 2,
            random.random() * self.screenshake - self.screenshake / 2,
        )
        self.screen.blit(
            pygame.transform.scale(self.display_2, self.screen.get_size()),
            screenshake_offset,
        )
        pygame.display.update()

    def run(self):
        """
        Main game loop that ties all update and render steps together.

        Args:
            None.

        Returns:
            None. Runs until the process exits.

        Dependencies:
            - _start_music()
            - update_transition_state()
            - update_camera_scroll()
            - spawn_leaf_particles()
            - stars.update(), stars.render()
            - tilemap.render()
            - update_enemies()
            - update_player()
            - update_projectiles()
            - update_sparks()
            - apply_display_mask()
            - update_particles()
            - handle_input()
            - draw_transition_circle()
            - present_frame()

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        self._start_music()
        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets["background"], (0, 0))
            self.screenshake = max(0, self.screenshake - 1)
            self.update_transition_state()
            self.update_camera_scroll()
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.spawn_leaf_particles()
            self.stars.update()
            self.stars.render(self.display_2, offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)
            self.update_enemies(render_scroll)
            self.update_player(render_scroll)
            self.update_projectiles(render_scroll)
            self.update_sparks(render_scroll)
            self.apply_display_mask()
            self.update_particles(render_scroll)
            self.handle_input()
            self.draw_transition_circle()
            self.present_frame()
            self.clock.tick(60)


if __name__ == "__main__":
    Game().run()
