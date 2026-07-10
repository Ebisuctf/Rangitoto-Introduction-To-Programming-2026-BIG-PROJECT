import pygame
import math
import random
from scripts.particle import Particles
from scripts.spark import Spark


class PhysicsEntity:
    """
    Base class for entities affected by physics and collisions.

    Args:
        game: Game instance providing assets and sounds.
        e_type (str): Entity type key (e.g. 'player', 'enemy').
        pos (tuple[float, float]): Starting position.
        size (tuple[int, int]): Width and height of the entity rectangle.

    Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

    Developed by: ______________________________
    """
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {"up": False, "down": False, "right": False, "left": False}
        self.action = ""
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action("idle")
        self.last_movement = [0, 0]

    def rect(self):
        """
        Get the pygame.Rect representing the entity's position and size.

        Args:
            None.

        Returns:
            pygame.Rect: Rectangle at current position with entity size.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: ______________________________
        """
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        """
        Change the current animation action for this entity.

        Args:
            action (str): New action name such as 'idle', 'run', 'jump'.

        Returns:
            None. Updates self.animation to a copy from game.assets.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + "/" + self.action].copy()

    def _apply_horizontal_movement(self, tilemap, frame_movement):
        """
        Apply horizontal movement and handle collisions with physics tiles.

        Args:
            tilemap (Tilemap): Tilemap used for collision rectangles.
            frame_movement (tuple[float, float]): Combined movement and velocity.

        Returns:
            None. Mutates self.pos and self.collisions.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rect_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions["right"] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions["left"] = True
                self.pos[0] = entity_rect.x

    def _apply_vertical_movement(self, tilemap, frame_movement):
        """
        Apply vertical movement and handle collisions with physics tiles.

        Args:
            tilemap (Tilemap): Tilemap used for collision rectangles.
            frame_movement (tuple[float, float]): Combined movement and velocity.

        Returns:
            None. Mutates self.pos and self.collisions.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rect_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                self.pos[1] = entity_rect.y

    def _apply_gravity(self):
        """
        Apply gravity to the entity's vertical velocity.

        Args:
            None.

        Returns:
            None. Caps falling speed at 5.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

    def update(self, tilemap, movement=(0, 0)):
        """
        Update the entity's position, collisions, gravity and animation.

        Args:
            tilemap (Tilemap): Tilemap providing collision rectangles.
            movement (tuple[float, float]): Desired movement from input.

        Returns:
            None.

        Bounty difficulty: ⭐⭐⭐⭐☆ (4/5)

        Developed by: ______________________________
        """
        self.collisions = {"up": False, "down": False, "right": False, "left": False}
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self._apply_horizontal_movement(tilemap, frame_movement)
        self._apply_vertical_movement(tilemap, frame_movement)

        self.last_movement = movement

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self._apply_gravity()

        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        """
        Render the entity's current animation frame.

        Args:
            surf (pygame.Surface): Surface to draw on.
            offset (tuple[int, int]): Camera offset for rendering.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        img = self.animation.img()
        pos = (
            self.pos[0] - offset[0] + self.anim_offset[0],
            self.pos[1] - offset[1] + self.anim_offset[1],
        )
        surf.blit(pygame.transform.flip(img, self.flip, False), pos)


class Enemy(PhysicsEntity):
    """
    Enemy that can walk, flip at edges and shoot projectiles at the player.

    Args:
        game: Game instance.
        pos (tuple[float, float]): Starting position.
        size (tuple[int, int]): Width and height.

    Bounty difficulty: ⭐⭐⭐⭐☆ (4/5)

    Developed by: ______________________________
    """
    def __init__(self, game, pos, size):
        super().__init__(game, "enemy", pos, size)
        self.walking = 0
        self.shoot_cooldown = 0

    def _update_walking_logic(self, tilemap, movement):
        """
        Handle enemy edge detection and walking direction changes.

        Args:
            tilemap (Tilemap): Tilemap for solid checks.
            movement (tuple[float, float]): Current movement.

        Returns:
            tuple[float, float]: Possibly modified movement.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        if self.walking:
            check_pos = (self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)
            if tilemap.solid_check(check_pos):
                if self.collisions["right"] or self.collisions["left"]:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
        elif random.random() < 0.01:
            self.walking = random.randint(60, 120)
        return movement

    def _maybe_shoot_at_player(self):
        """
        Possibly shoot a projectile towards the player if in line of sight.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐⭐⭐⭐☆ (4/5)

        Developed by: ______________________________
        """
        # Don't shoot while walking or if we're still on cooldown
        if self.walking:
            return
        if self.shoot_cooldown > 0:
            return

        # Distance to player
        dis = (self.game.player.pos[0] - self.pos[0],
               self.game.player.pos[1] - self.pos[1])

        # Only shoot if roughly horizontally aligned
        if abs(dis[1]) < 16:
            # Player to the left, enemy facing left
            if self.flip and dis[0] < 0:
                self.game.sfx["shoot"].play()
                self.game.projectiles.append(
                    [[self.rect().centerx - 7, self.rect().centery], -1.5, 0]
                )
                for _ in range(4):
                    self.game.sparks.append(
                        Spark(
                            self.game.projectiles[-1][0],
                                random.random() - 0.5 + math.pi,
                            2 + random.random(),
                        )
                    )
                self.shoot_cooldown = 30  # wait ~0.5s before next shot

            # Player to the right, enemy facing right
            elif not self.flip and dis[0] > 0:
                self.game.sfx["shoot"].play()
                self.game.projectiles.append(
                    [[self.rect().centerx + 7, self.rect().centery], 1.5, 0]
                )
                for _ in range(4):
                    self.game.sparks.append(
                        Spark(
                            self.game.projectiles[-1][0],
                            random.random() - 0.5,
                            2 + random.random(),
                        )
                    )
                self.shoot_cooldown = 30  # wait ~0.5s before next shot

    def _handle_dash_collision(self):
        """
        Handle being destroyed when the player dashes through the enemy.

        Args:
            None.

        Returns:
            bool: True if the enemy was destroyed.

        Bounty difficulty: ⭐⭐⭐⭐☆ (4/5)

        Developed by: ______________________________
        """
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake = max(16, self.game.screenshake)
                self.game.sfx["hit"].play()
                for _ in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(
                        Particles(
                            self.game,
                            "particle",
                            self.rect().center,
                            velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5],
                            frame=random.randint(0, 7),
                        )
                    )
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True
        return False

    def update(self, tilemap, movement=(0, 0)):
        """
        Update enemy walking logic, shooting, physics and actions.

        Args:
            tilemap (Tilemap): Tilemap used for collisions and solid checks.
            movement (tuple[float, float]): X/Y movement.

        Returns:
            bool: True if the enemy was destroyed by a dash.

        Bounty difficulty: ⭐⭐⭐⭐☆ (4/5)

        Developed by: ______________________________
        """
        movement = self._update_walking_logic(tilemap, movement)

        # NEW: tick down cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self._maybe_shoot_at_player()
        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action("run")
        else:
            self.set_action("idle")

        return self._handle_dash_collision()

    def render(self, surf, offset=(0, 0)):
        """
        Render enemy and its gun sprite.

        Args:
            surf (pygame.Surface): Surface to draw on.
            offset (tuple[int, int]): Camera offset.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        super().render(surf, offset=offset)
        gun_img = self.game.assets["gun"]
        if self.flip:
            pos = (
                self.rect().centerx - 4 - gun_img.get_width() - offset[0],
                self.rect().centery - offset[1],
            )
            surf.blit(pygame.transform.flip(gun_img, True, False), pos)
        else:
            pos = (
                self.rect().centerx + 4 - offset[0],
                self.rect().centery - offset[1],
            )
            surf.blit(gun_img, pos)


class Player(PhysicsEntity):
    """
    Controllable player character with jumping, wall-sliding and dashing.

    Args:
        game: Game instance.
        pos (tuple[float, float]): Starting position.
        size (tuple[int, int]): Width and height.

    Bounty difficulty: ⭐⭐⭐⭐☆ (4/5)

    Developed by: ______________________________
    """
    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.air_time = 0
        self.jumps = 2
        self.wall_slide = False
        self.dashing = 0

    def _update_air_state(self):
        """
        Update air time and handle falling death.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        self.air_time += 1
        if self.air_time > 180:
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)
                self.game.sfx["hit"].play()
            self.game.dead += 1

    def _reset_on_ground(self):
        """
        Reset jump counters when landing on the ground.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐☆☆☆☆ (1/5)

        Developed by: Amit Sahaf - 197821
        """
        if self.collisions["down"]:
            self.air_time = 0
            self.jumps = 2

    def _update_wall_slide_state(self):
        """
        Determine whether the player is wall-sliding.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        self.wall_slide = False
        if (self.collisions["right"] or self.collisions["left"]) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions["right"]:
                self.flip = False
            else:
                self.flip = True
            self.set_action("wall_slide")

    def _update_ground_actions(self, movement):
        """
        Choose idle/run/jump animations based on movement and air state.

        Args:
            movement (tuple[float, float]): Current movement.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action("jump")
            elif movement[0] != 0:
                self.set_action("run")
            else:
                self.set_action("idle")

    def _spawn_dash_burst_particles(self):
        """
        Spawn burst particles at the start and end of a dash.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        if abs(self.dashing) in {60, 50}:
            for _ in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(
                    Particles(self.game, "particle", self.rect().center, velocity=pvelocity, frame=random.randint(0, 7))
                )

    def _update_dash_state(self):
        """
        Update dash timer and adjust horizontal velocity.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)

        if abs(self.dashing) > 50:
            direction = abs(self.dashing) / self.dashing
            self.velocity[0] = direction * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
                pvelocity = [direction * random.random() * 3, 0]
                self.game.particles.append(
                    Particles(self.game, "particle", self.rect().center, velocity=pvelocity, frame=random.randint(0, 7))
                )

    def _apply_horizontal_friction(self):
        """
        Apply friction to horizontal velocity when not dashing strongly.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def update(self, tilemap, movement=(0, 0)):
        """
        Update player physics, actions, dash and animations.

        Args:
            tilemap (Tilemap): Tilemap for collision.
            movement (tuple[float, float]): Input movement.

        Returns:
            None.

        Bounty difficulty: ⭐⭐⭐⭐☆ (4/5)

        Developed by: ______________________________
        """
        super().update(tilemap, movement=movement)
        self._update_air_state()
        self._reset_on_ground()
        self._update_wall_slide_state()
        self._update_ground_actions(movement)
        self._spawn_dash_burst_particles()
        self._update_dash_state()
        self._apply_horizontal_friction()

    def render(self, surf, offset=(0, 0)):
        """
        Render the player unless in the strong dash phase.

        Args:
            surf (pygame.Surface): Surface to draw on.
            offset (tuple[int, int]): Camera offset.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)

    def jump(self):
        """
        Attempt to perform a jump or wall-jump.

        Args:
            None.

        Returns:
            bool: True if a jump was performed.

        Bounty difficulty: ⭐⭐⭐☆☆ (3/5)

        Developed by: ______________________________
        """
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
        return False

    def dash(self):
        """
        Start a dash in the current facing direction if not already dashing.

        Args:
            None.

        Returns:
            None.

        Bounty difficulty: ⭐⭐☆☆☆ (2/5)

        Developed by: ______________________________
        """
        if not self.dashing:
            self.game.sfx["dash"].play()
            self.dashing = -60 if self.flip else 60
