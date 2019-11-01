from __future__ import division

import pygame as pg
from .. import setup, tools
from .. import constants as c
from .. import game_sound
from .. components import mario
from .. components import collider
from .. components import bricks
from .. components import coin_box
from .. components import enemies
from .. components import checkpoint
from .. components import flagpole
from .. components import info
from .. components import score
from .. components import castle_flag

class Level12(tools._State):
    def __init__(self):
        tools._State.__init__(self)

    def startup(self, current_time, persist):
        #call when state object is made
        self.game_info = persist
        self.persist = self.game_info
        self.game_info[c.CURRENT_TIME] = current_time
        self.game_info[c.LEVEL_STATE] = c.NOT_FROZEN
        self.game_info[c.MARIO_DEAD] = False
        self.state = c.NOT_FROZEN
        self.death_timer = 0
        self.flag_timer = 0
        self.flag_score = None
        self.flag_score_total = 0
        self.moving_score_list = []
        self.overhead_info_display = info.OverheadInfo(self.game_info, c.LEVEL)
        self.sound_manager = game_sound.Sound(self.overhead_info_display)
        self.setup_background()
        self.setup_ground()
        self.setup_pipes()
        self.setup_steps()
        self.setup_bricks()
        self.setup_coin_boxes()
        self.setup_flag_pole()
        self.setup_enemies()
        self.setup_mario()
        self.setup_checkpoints()
        self.setup_spritegroups()

    def setup_background(self):
        #sets the background image, rect and scales it
        self.background = setup.GFX['level_12']
        self.back_rect = self.background.get_rect()
        self.background = pg.transform.scale(self.background,
                                  (int(self.back_rect.width*c.BACKGROUND_MULTIPLER),
                                  int(self.back_rect.height*c.BACKGROUND_MULTIPLER)))
        self.back_rect = self.background.get_rect()
        width = self.back_rect.width
        height = self.back_rect.height
        self.level = pg.Surface((width, height)).convert()
        self.level_rect = self.level.get_rect()
        self.viewport = setup.SCREEN.get_rect(bottom=self.level_rect.bottom)
        self.viewport.x = self.game_info[c.CAMERA_START_X]

    def setup_ground(self):
        # Need to implement
        ground_rect1 = collider.Collider(0, c.GROUND_HEIGHT, 1263 * c.BACKGROUND_MULTIPLER, 60)
        ground_rect2 = collider.Collider(1328* c.BACKGROUND_MULTIPLER, c.GROUND_HEIGHT, 591 * c.BACKGROUND_MULTIPLER, 60)
        ground_rect3 = collider.Collider(1953* c.BACKGROUND_MULTIPLER, c.GROUND_HEIGHT, 32 * c.BACKGROUND_MULTIPLER, 60)
        ground_rect4 = collider.Collider(2017* c.BACKGROUND_MULTIPLER, c.GROUND_HEIGHT, 192 * c.BACKGROUND_MULTIPLER, 60)
        ground_rect5 = collider.Collider(2321* c.BACKGROUND_MULTIPLER, c.GROUND_HEIGHT, 126* c.BACKGROUND_MULTIPLER, 60)
        ground_rect6 = collider.Collider(2560* c.BACKGROUND_MULTIPLER, 152, 96* c.BACKGROUND_MULTIPLER, 60)
        self.ground_group = pg.sprite.Group(ground_rect1, ground_rect2, ground_rect3, ground_rect4, ground_rect5,
                                            ground_rect6)

    def setup_pipes(self):
        # Need to implement
        pass

    def setup_steps(self):
        # Need to implement
        pass

    def setup_bricks(self):
        # Need to implement
        pass

    def setup_coin_boxes(self):
        # Need to implement
        pass

    def setup_enemies(self):
        # Need to implement
        pass

    def setup_mario(self):
        #places mario at the beginning of map
        self.mario = mario.Mario()
        self.mario.rect.x = self.viewport.x + 110
        self.mario.rect.bottom = c.GROUND_HEIGHT

    def setup_checkpoints(self):
        # Need ti implement when the enemies spawn
        pass

    def setup_spritegroups(self):
        #sprite groups
        self.sprites_about_to_die_group = pg.sprite.Group()
        self.shell_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()
        self.ground_step_pipe_group = pg.sprite.Group(self.ground_group,self.pipe_group,self.step_group)
        self.mario_and_enemy_group = pg.sprite.Group(self.mario,self.enemy_group)

    def update(self, surface, keys, current_time):
        #updates Entire level using states.  Called by control object
        self.game_info[c.CURRENT_TIME] = self.current_time = current_time
        self.handle_states(keys)
        self.check_if_time_out()
        self.blit_everything(surface)
        self.sound_manager.update(self.game_info, self.mario)

    def handle_states(self, keys):
        # if the level is in a FROZEN state, only mario updates
        if self.state == c.FROZEN:
            self.update_during_transition_state(keys)
        elif self.state == c.NOT_FROZEN:
            self.update_all_sprites(keys)
        elif self.state == c.IN_CASTLE:
            self.update_while_in_castle()
        elif self.state == c.FLAG_AND_FIREWORKS:
            self.update_flag_and_fireworks()

    def update_during_transition_state(self, keys):
        # Updates mario in a transition state, checks if he leaves transition state or dies to change the level state
        self.mario.update(keys, self.game_info, self.powerup_group)
        for score in self.moving_score_list:
            score.update(self.moving_score_list, self.game_info)
        if self.flag_score:
            self.flag_score.update(None, self.game_info)
            self.check_to_add_flag_score()
        self.coin_box_group.update(self.game_info)
        self.flag_pole_group.update(self.game_info)
        self.check_if_mario_in_transition_state()
        self.check_flag()
        self.check_for_mario_death()
        self.overhead_info_display.update(self.game_info, self.mario)

    def check_if_mario_in_transition_state(self):
        # if mario is in a transition state, the level will be in a FREEZE state
        if self.mario.in_transition_state:
            self.game_info[c.LEVEL_STATE] = self.state = c.FROZEN
        elif self.mario.in_transition_state == False:
            if self.state == c.FROZEN:
                self.game_info[c.LEVEL_STATE] = self.state = c.NOT_FROZEN

    def update_all_sprites(self, keys):
        # updates the location of all sprites on the screen.
        self.mario.update(keys, self.game_info, self.powerup_group)
        for score in self.moving_score_list:
            score.update(self.moving_score_list, self.game_info)
        if self.flag_score:
            self.flag_score.update(None, self.game_info)
            self.check_to_add_flag_score()
        self.flag_pole_group.update()
        self.check_points_check()
        self.enemy_group.update(self.game_info)
        self.sprites_about_to_die_group.update(self.game_info, self.viewport)
        self.shell_group.update(self.game_info)
        self.brick_group.update()
        self.coin_box_group.update(self.game_info)
        self.powerup_group.update(self.game_info, self.viewport)
        self.coin_group.update(self.game_info, self.viewport)
        self.brick_pieces_group.update()
        self.adjust_sprite_positions()
        self.check_if_mario_in_transition_state()
        self.check_for_mario_death()
        self.update_viewport()
        self.overhead_info_display.update(self.game_info, self.mario)

    def check_points_check(self):
        # Detect if checkpoint collision occurs, delete checkpoint, add enemies to enemy group
        checkpoint = pg.sprite.spritecollideany(self.mario, self.check_point_group)
        if checkpoint:
            checkpoint.kill()
            for i in range(1, 11):
                if checkpoint.name == str(i):
                    for index, enemy in enumerate(self.enemy_group_list[i - 1]):
                        enemy.rect.x = self.viewport.right + (index * 60)
                    self.enemy_group.add(self.enemy_group_list[i - 1])
            if checkpoint.name == '11':
                self.mario.state = c.FLAGPOLE
                self.mario.invincible = False
                self.mario.flag_pole_right = checkpoint.rect.right
                if self.mario.rect.bottom < self.flag.rect.y:
                    self.mario.rect.bottom = self.flag.rect.y
                self.flag.state = c.SLIDE_DOWN
                self.create_flag_points()
            elif checkpoint.name == '12':
                self.state = c.IN_CASTLE
                self.mario.kill()
                self.mario.state == c.STAND
                self.mario.in_castle = True
                self.overhead_info_display.state = c.FAST_COUNT_DOWN
            elif checkpoint.name == 'secret_mushroom' and self.mario.y_vel < 0:
                mushroom_box = coin_box.Coin_box(checkpoint.rect.x, checkpoint.rect.bottom - 40,
                                                 '1up_mushroom', self.powerup_group)
                mushroom_box.start_bump(self.moving_score_list)
                self.coin_box_group.add(mushroom_box)
                self.mario.y_vel = 7
                self.mario.rect.y = mushroom_box.rect.bottom
                self.mario.state = c.FALL
            self.mario_and_enemy_group.add(self.enemy_group)

    def adjust_sprite_positions(self):
        # Adjusts sprites by their x and y velocities and collisions
        self.adjust_mario_position()
        self.adjust_enemy_position()
        self.adjust_shell_position()
        self.adjust_powerup_position()

    def adjust_mario_position(self):
        # adjusts Mario's position based on his x, y velocities and potential collisions
        self.last_x_position = self.mario.rect.right
        self.mario.rect.x += round(self.mario.x_vel)
        self.check_mario_x_collisions()
        if self.mario.in_transition_state == False:
            self.mario.rect.y += round(self.mario.y_vel)
            self.check_mario_y_collisions()
        if self.mario.rect.x < (self.viewport.x + 5):
            self.mario.rect.x = (self.viewport.x + 5)

    def check_mario_x_collisions(self):
        # Check for collisions after Mario moves on x axis
        collider = pg.sprite.spritecollideany(self.mario, self.ground_step_pipe_group)
        coin_box = pg.sprite.spritecollideany(self.mario, self.coin_box_group)
        brick = pg.sprite.spritecollideany(self.mario, self.brick_group)
        enemy = pg.sprite.spritecollideany(self.mario, self.enemy_group)
        shell = pg.sprite.spritecollideany(self.mario, self.shell_group)
        powerup = pg.sprite.spritecollideany(self.mario, self.powerup_group)
        if coin_box:
            self.adjust_mario_for_x_collisions(coin_box)
        elif brick:
            self.adjust_mario_for_x_collisions(brick)
        elif collider:
            self.adjust_mario_for_x_collisions(collider)
        elif enemy:
            if self.mario.invincible:
                setup.SFX['kick'].play()
                self.game_info[c.SCORE] += 100
                self.moving_score_list.append(
                    score.Score(self.mario.rect.right - self.viewport.x, self.mario.rect.y, 100))
                enemy.kill()
                enemy.start_death_jump(c.RIGHT)
                self.sprites_about_to_die_group.add(enemy)
            elif self.mario.big:
                setup.SFX['pipe'].play()
                self.mario.fire = False
                self.mario.y_vel = -1
                self.mario.state = c.BIG_TO_SMALL
                self.convert_fireflowers_to_mushrooms()
            elif self.mario.hurt_invincible:
                pass
            else:
                self.mario.start_death_jump(self.game_info)
                self.state = c.FROZEN
        elif shell:
            self.adjust_mario_for_x_shell_collisions(shell)
        elif powerup:
            if powerup.name == c.STAR:
                self.game_info[c.SCORE] += 1000
                self.moving_score_list.append(
                    score.Score(self.mario.rect.centerx - self.viewport.x, self.mario.rect.y, 1000))
                self.mario.invincible = True
                self.mario.invincible_start_timer = self.current_time
            elif powerup.name == c.MUSHROOM:
                setup.SFX['powerup'].play()
                self.game_info[c.SCORE] += 1000
                self.moving_score_list.append(
                    score.Score(self.mario.rect.centerx - self.viewport.x, self.mario.rect.y - 20, 1000))
                self.mario.y_vel = -1
                self.mario.state = c.SMALL_TO_BIG
                self.mario.in_transition_state = True
                self.convert_mushrooms_to_fireflowers()
            elif powerup.name == c.LIFE_MUSHROOM:
                self.moving_score_list.append(
                    score.Score(powerup.rect.right - self.viewport.x, powerup.rect.y, c.ONEUP))
                self.game_info[c.LIVES] += 1
                setup.SFX['one_up'].play()
            elif powerup.name == c.FIREFLOWER:
                setup.SFX['powerup'].play()
                self.game_info[c.SCORE] += 1000
                self.moving_score_list.append(
                    score.Score(self.mario.rect.centerx - self.viewport.x, self.mario.rect.y, 1000))
                if self.mario.big and self.mario.fire == False:
                    self.mario.state = c.BIG_TO_FIRE
                    self.mario.in_transition_state = True
                elif self.mario.big == False:
                    self.mario.state = c.SMALL_TO_BIG
                    self.mario.in_transition_state = True
                    self.convert_mushrooms_to_fireflowers()
            if powerup.name != c.FIREBALL:
                powerup.kill()

    def convert_mushrooms_to_fireflowers(self):
        # When Mario becomees big, converts all fireflower powerups to mushroom powerups
        for brick in self.brick_group:
            if brick.contents == c.MUSHROOM:
                brick.contents = c.FIREFLOWER
        for coin_box in self.coin_box_group:
            if coin_box.contents == c.MUSHROOM:
                coin_box.contents = c.FIREFLOWER

    def convert_fireflowers_to_mushrooms(self):
        # When Mario becomes small, converts all mushroom powerups to fireflower powerups
        for brick in self.brick_group:
            if brick.contents == c.FIREFLOWER:
                brick.contents = c.MUSHROOM
        for coin_box in self.coin_box_group:
            if coin_box.contents == c.FIREFLOWER:
                coin_box.contents = c.MUSHROOM

    def adjust_mario_for_x_collisions(self, collider):
        # Puts Mario flush next to the collider after moving on x axis
        if self.mario.rect.x < collider.rect.x:
            self.mario.rect.right = collider.rect.left
        else:
            self.mario.rect.left = collider.rect.right
        self.mario.x_vel = 0

    def adjust_mario_for_x_shell_collisions(self, shell):
        # Deals with Mario if he hits a shell moving on the x axis
        if shell.state == c.JUMPED_ON:
            if self.mario.rect.x < shell.rect.x:
                self.game_info[c.SCORE] += 400
                self.moving_score_list.append(
                    score.Score(shell.rect.centerx - self.viewport.x, shell.rect.y, 400))
                self.mario.rect.right = shell.rect.left
                shell.direction = c.RIGHT
                shell.x_vel = 5
                shell.rect.x += 5
            else:
                self.mario.rect.left = shell.rect.right
                shell.direction = c.LEFT
                shell.x_vel = -5
                shell.rect.x += -5
            shell.state = c.SHELL_SLIDE
        elif shell.state == c.SHELL_SLIDE:
            if self.mario.big and not self.mario.invincible:
                self.mario.state = c.BIG_TO_SMALL
            elif self.mario.invincible:
                self.game_info[c.SCORE] += 200
                self.moving_score_list.append(
                    score.Score(shell.rect.right - self.viewport.x, shell.rect.y, 200))
                shell.kill()
                self.sprites_about_to_die_group.add(shell)
                shell.start_death_jump(c.RIGHT)
            else:
                if not self.mario.hurt_invincible and not self.mario.invincible:
                    self.state = c.FROZEN
                    self.mario.start_death_jump(self.game_info)

    def check_mario_y_collisions(self):
        # checks for collisions when Mario moves along y-axis
        ground_step_or_pipe = pg.sprite.spritecollideany(self.mario, self.ground_step_pipe_group)
        enemy = pg.sprite.spritecollideany(self.mario, self.enemy_group)
        shell = pg.sprite.spritecollideany(self.mario, self.shell_group)
        brick = pg.sprite.spritecollideany(self.mario, self.brick_group)
        coin_box = pg.sprite.spritecollideany(self.mario, self.coin_box_group)
        powerup = pg.sprite.spritecollideany(self.mario, self.powerup_group)
        brick, coin_box = self.prevent_collision_conflict(brick, coin_box)
        if coin_box:
            self.adjust_mario_for_y_coin_box_collisions(coin_box)
        elif brick:
            self.adjust_mario_for_y_brick_collisions(brick)
        elif ground_step_or_pipe:
            self.adjust_mario_for_y_ground_pipe_collisions(ground_step_or_pipe)
        elif enemy:
            if self.mario.invincible:
                setup.SFX['kick'].play()
                enemy.kill()
                self.sprites_about_to_die_group.add(enemy)
                enemy.start_death_jump(c.RIGHT)
            else:
                self.adjust_mario_for_y_enemy_collisions(enemy)
        elif shell:
            self.adjust_mario_for_y_shell_collisions(shell)
        elif powerup:
            if powerup.name == c.STAR:
                setup.SFX['powerup'].play()
                powerup.kill()
                self.mario.invincible = True
                self.mario.invincible_start_timer = self.current_time
        self.test_if_mario_is_falling()

    def prevent_collision_conflict(self, obstacle1, obstacle2):
        # Allows collisions only for the item closest to marios centerx
        if obstacle1 and obstacle2:
            obstacle1_distance = self.mario.rect.centerx - obstacle1.rect.centerx
            if obstacle1_distance < 0:
                obstacle1_distance *= -1
            obstacle2_distance = self.mario.rect.centerx - obstacle2.rect.centerx
            if obstacle2_distance < 0:
                obstacle2_distance *= -1
            if obstacle1_distance < obstacle2_distance:
                obstacle2 = False
            else:
                obstacle1 = False
        return obstacle1, obstacle2

    def adjust_mario_for_y_coin_box_collisions(self, coin_box):
        # mario collisions with coin boxes on the y-axis
        if self.mario.rect.y > coin_box.rect.y:
            if coin_box.state == c.RESTING:
                if coin_box.contents == c.COIN:
                    self.game_info[c.SCORE] += 200
                    coin_box.start_bump(self.moving_score_list)
                    if coin_box.contents == c.COIN:
                        self.game_info[c.COIN_TOTAL] += 1
                else:
                    coin_box.start_bump(self.moving_score_list)
            elif coin_box.state == c.OPENED:
                pass
            setup.SFX['bump'].play()
            self.mario.y_vel = 7
            self.mario.rect.y = coin_box.rect.bottom
            self.mario.state = c.FALL
        else:
            self.mario.y_vel = 0
            self.mario.rect.bottom = coin_box.rect.top
            self.mario.state = c.WALK

    def adjust_mario_for_y_brick_collisions(self, brick):
        # Mario collisions with bricks on y-axis
        if self.mario.rect.y > brick.rect.y:
            if brick.state == c.RESTING:
                if self.mario.big and brick.contents is None:
                    setup.SFX['brick_smash'].play()
                    self.check_if_enemy_on_brick(brick)
                    brick.kill()
                    self.brick_pieces_group.add(
                        bricks.BrickPiece(brick.rect.x, brick.rect.y - (brick.rect.height / 2), -2, -12),
                        bricks.BrickPiece(brick.rect.right, brick.rect.y - (brick.rect.height / 2), 2, -12),
                        bricks.BrickPiece(brick.rect.x, brick.rect.y, -2, -6),
                        bricks.BrickPiece(brick.rect.right, brick.rect.y, 2, -6))
                else:
                    setup.SFX['bump'].play()
                    if brick.coin_total > 0:
                        self.game_info[c.COIN_TOTAL] += 1
                        self.game_info[c.SCORE] += 200
                    self.check_if_enemy_on_brick(brick)
                    brick.start_bump(self.moving_score_list)
            elif brick.state == c.OPENED:
                setup.SFX['bump'].play()
            self.mario.y_vel = 7
            self.mario.rect.y = brick.rect.bottom
            self.mario.state = c.FALL
        else:
            self.mario.y_vel = 0
            self.mario.rect.bottom = brick.rect.top
            self.mario.state = c.WALK

    def check_if_enemy_on_brick(self, brick):
        # kills enemy if on bumped or broken brick
        brick.rect.y -= 5
        enemy = pg.sprite.spritecollideany(brick, self.enemy_group)
        if enemy:
            setup.SFX['kick'].play()
            self.game_info[c.SCORE] += 100
            self.moving_score_list.append(
                score.Score(enemy.rect.centerx - self.viewport.x, enemy.rect.y, 100))
            enemy.kill()
            self.sprites_about_to_die_group.add(enemy)
            if self.mario.rect.centerx > brick.rect.centerx:
                enemy.start_death_jump('right')
            else:
                enemy.start_death_jump('left')
        brick.rect.y += 5

    def adjust_mario_for_y_ground_pipe_collisions(self, collider):
        # Mario collision with pipes on y-axis
        if collider.rect.bottom > self.mario.rect.bottom:
            self.mario.y_vel = 0
            self.mario.rect.bottom = collider.rect.top
            if self.mario.state == c.END_OF_LEVEL_FALL:
                self.mario.state = c.WALKING_TO_CASTLE
            else:
                self.mario.state = c.WALK
        elif collider.rect.top < self.mario.rect.top:
            self.mario.y_vel = 7
            self.mario.rect.top = collider.rect.bottom
            self.mario.state = c.FALL

    def test_if_mario_is_falling(self):
        # changes Mario to a FALL state if more than a pixel above a pipe, ground, step or box
        self.mario.rect.y += 1
        test_collide_group = pg.sprite.Group(self.ground_step_pipe_group, self.brick_group, self.coin_box_group)
        if pg.sprite.spritecollideany(self.mario, test_collide_group) is None:
            if self.mario.state != c.JUMP \
                    and self.mario.state != c.DEATH_JUMP \
                    and self.mario.state != c.SMALL_TO_BIG \
                    and self.mario.state != c.BIG_TO_FIRE \
                    and self.mario.state != c.BIG_TO_SMALL \
                    and self.mario.state != c.FLAGPOLE \
                    and self.mario.state != c.WALKING_TO_CASTLE \
                    and self.mario.state != c.END_OF_LEVEL_FALL:
                self.mario.state = c.FALL
            elif self.mario.state == c.WALKING_TO_CASTLE or \
                    self.mario.state == c.END_OF_LEVEL_FALL:
                self.mario.state = c.END_OF_LEVEL_FALL
        self.mario.rect.y -= 1

    def adjust_mario_for_y_enemy_collisions(self, enemy):
        # mario collisions with all enemies on y-axis
        if self.mario.y_vel > 0:
            setup.SFX['stomp'].play()
            self.game_info[c.SCORE] += 100
            self.moving_score_list.append(
                score.Score(enemy.rect.centerx - self.viewport.x, enemy.rect.y, 100))
            enemy.state = c.JUMPED_ON
            enemy.kill()
            if enemy.name == c.GOOMBA:
                enemy.death_timer = self.current_time
                self.sprites_about_to_die_group.add(enemy)
            elif enemy.name == c.KOOPA:
                self.shell_group.add(enemy)
            self.mario.rect.bottom = enemy.rect.top
            self.mario.state = c.JUMP
            self.mario.y_vel = -7

    def adjust_mario_for_y_shell_collisions(self, shell):
        # Mario collisions with Koopas in their shells on y axis
        if self.mario.y_vel > 0:
            self.game_info[c.SCORE] += 400
            self.moving_score_list.append(
                score.Score(self.mario.rect.centerx - self.viewport.x, self.mario.rect.y, 400))
            if shell.state == c.JUMPED_ON:
                setup.SFX['kick'].play()
                shell.state = c.SHELL_SLIDE
                if self.mario.rect.centerx < shell.rect.centerx:
                    shell.direction = c.RIGHT
                    shell.rect.left = self.mario.rect.right + 5
                else:
                    shell.direction = c.LEFT
                    shell.rect.right = self.mario.rect.left - 5
            else:
                shell.state = c.JUMPED_ON

    def adjust_enemy_position(self):
        # moves all enemies along the x, y axes and check for collisions
        for enemy in self.enemy_group:
            enemy.rect.x += enemy.x_vel
            self.check_enemy_x_collisions(enemy)
            enemy.rect.y += enemy.y_vel
            self.check_enemy_y_collisions(enemy)
            self.delete_if_off_screen(enemy)

    def check_enemy_x_collisions(self, enemy):
        # Enemy collisions on x axis. Removes enemy from group to check against other enemies then adds it back
        enemy.kill()
        collider = pg.sprite.spritecollideany(enemy, self.ground_step_pipe_group)
        enemy_collider = pg.sprite.spritecollideany(enemy, self.enemy_group)
        if collider:
            if enemy.direction == c.RIGHT:
                enemy.rect.right = collider.rect.left
                enemy.direction = c.LEFT
                enemy.x_vel = -2
            elif enemy.direction == c.LEFT:
                enemy.rect.left = collider.rect.right
                enemy.direction = c.RIGHT
                enemy.x_vel = 2
        elif enemy_collider:
            if enemy.direction == c.RIGHT:
                enemy.rect.right = enemy_collider.rect.left
                enemy.direction = c.LEFT
                enemy_collider.direction = c.RIGHT
                enemy.x_vel = -2
                enemy_collider.x_vel = 2
            elif enemy.direction == c.LEFT:
                enemy.rect.left = enemy_collider.rect.right
                enemy.direction = c.RIGHT
                enemy_collider.direction = c.LEFT
                enemy.x_vel = 2
                enemy_collider.x_vel = -2
        self.enemy_group.add(enemy)
        self.mario_and_enemy_group.add(self.enemy_group)

    def check_enemy_y_collisions(self, enemy):
        # Enemy collisions on the y axis
        collider = pg.sprite.spritecollideany(enemy, self.ground_step_pipe_group)
        brick = pg.sprite.spritecollideany(enemy, self.brick_group)
        coin_box = pg.sprite.spritecollideany(enemy, self.coin_box_group)
        if collider:
            if enemy.rect.bottom > collider.rect.bottom:
                enemy.y_vel = 7
                enemy.rect.top = collider.rect.bottom
                enemy.state = c.FALL
            elif enemy.rect.bottom < collider.rect.bottom:
                enemy.y_vel = 0
                enemy.rect.bottom = collider.rect.top
                enemy.state = c.WALK
        elif brick:
            if brick.state == c.BUMPED:
                enemy.kill()
                self.sprites_about_to_die_group.add(enemy)
                if self.mario.rect.centerx > brick.rect.centerx:
                    enemy.start_death_jump('right')
                else:
                    enemy.start_death_jump('left')
            elif enemy.rect.x > brick.rect.x:
                enemy.y_vel = 7
                enemy.rect.top = brick.rect.bottom
                enemy.state = c.FALL
            else:
                enemy.y_vel = 0
                enemy.rect.bottom = brick.rect.top
                enemy.state = c.WALK
        elif coin_box:
            if coin_box.state == c.BUMPED:
                self.game_info[c.SCORE] += 100
                self.moving_score_list.append(
                    score.Score(enemy.rect.centerx - self.viewport.x, enemy.rect.y, 100))
                enemy.kill()
                self.sprites_about_to_die_group.add(enemy)
                if self.mario.rect.centerx > coin_box.rect.centerx:
                    enemy.start_death_jump('right')
                else:
                    enemy.start_death_jump('left')
            elif enemy.rect.x > coin_box.rect.x:
                enemy.y_vel = 7
                enemy.rect.top = coin_box.rect.bottom
                enemy.state = c.FALL
            else:
                enemy.y_vel = 0
                enemy.rect.bottom = coin_box.rect.top
                enemy.state = c.WALK
        else:
            enemy.rect.y += 1
            test_group = pg.sprite.Group(self.ground_step_pipe_group, self.coin_box_group, self.brick_group)
            if pg.sprite.spritecollideany(enemy, test_group) is None:
                if enemy.state != c.JUMP:
                    enemy.state = c.FALL
            enemy.rect.y -= 1

    def adjust_shell_position(self):
        # moves any koopa in a shell along the x, y axes and checks for collision
        for shell in self.shell_group:
            shell.rect.x += shell.x_vel
            self.check_shell_x_collisions(shell)
            shell.rect.y += shell.y_vel
            self.check_shell_y_collisions(shell)
            self.delete_if_off_screen(shell)

    def check_shell_x_collisions(self, shell):
        # Shell collisions along x axis
        collider = pg.sprite.spritecollideany(shell, self.ground_step_pipe_group)
        enemy = pg.sprite.spritecollideany(shell, self.enemy_group)
        if collider:
            setup.SFX['bump'].play()
            if shell.x_vel > 0:
                shell.direction = c.LEFT
                shell.rect.right = collider.rect.left
            else:
                shell.direction = c.RIGHT
                shell.rect.left = collider.rect.right
        if enemy:
            setup.SFX['kick'].play()
            self.game_info[c.SCORE] += 100
            self.moving_score_list.append(
                score.Score(enemy.rect.right - self.viewport.x, enemy.rect.y, 100))
            enemy.kill()
            self.sprites_about_to_die_group.add(enemy)
            enemy.start_death_jump(shell.direction)

    def check_shell_y_collisions(self, shell):
        # Shell collisions along y axis
        collider = pg.sprite.spritecollideany(shell, self.ground_step_pipe_group)
        if collider:
            shell.y_vel = 0
            shell.rect.bottom = collider.rect.top
            shell.state = c.SHELL_SLIDE
        else:
            shell.rect.y += 1
            if pg.sprite.spritecollideany(shell, self.ground_step_pipe_group) is None:
                shell.state = c.FALL
            shell.rect.y -= 1

    def adjust_powerup_position(self):
        # Moves mushrooms, stars and fireballs along the x, y axes
        for powerup in self.powerup_group:
            if powerup.name == c.MUSHROOM:
                self.adjust_mushroom_position(powerup)
            elif powerup.name == c.STAR:
                self.adjust_star_position(powerup)
            elif powerup.name == c.FIREBALL:
                self.adjust_fireball_position(powerup)
            elif powerup.name == '1up_mushroom':
                self.adjust_mushroom_position(powerup)

    def adjust_mushroom_position(self, mushroom):
        # Moves mushroom along the x, y axes
        if mushroom.state != c.REVEAL:
            mushroom.rect.x += mushroom.x_vel
            self.check_mushroom_x_collisions(mushroom)
            mushroom.rect.y += mushroom.y_vel
            self.check_mushroom_y_collisions(mushroom)
            self.delete_if_off_screen(mushroom)

    def check_mushroom_x_collisions(self, mushroom):
        # Mushroom collisions along x axis
        collider = pg.sprite.spritecollideany(mushroom, self.ground_step_pipe_group)
        brick = pg.sprite.spritecollideany(mushroom, self.brick_group)
        coin_box = pg.sprite.spritecollideany(mushroom, self.coin_box_group)
        if collider:
            self.adjust_mushroom_for_collision_x(mushroom, collider)
        elif brick:
            self.adjust_mushroom_for_collision_x(mushroom, brick)
        elif coin_box:
            self.adjust_mushroom_for_collision_x(mushroom, coin_box)

    def check_mushroom_y_collisions(self, mushroom):
        # mushroom collisions along y axis
        collider = pg.sprite.spritecollideany(mushroom, self.ground_step_pipe_group)
        brick = pg.sprite.spritecollideany(mushroom, self.brick_group)
        coin_box = pg.sprite.spritecollideany(mushroom, self.coin_box_group)
        if collider:
            self.adjust_mushroom_for_collision_y(mushroom, collider)
        elif brick:
            self.adjust_mushroom_for_collision_y(mushroom, brick)
        elif coin_box:
            self.adjust_mushroom_for_collision_y(mushroom, coin_box)
        else:
            self.check_if_falling(mushroom, self.ground_step_pipe_group)
            self.check_if_falling(mushroom, self.brick_group)
            self.check_if_falling(mushroom, self.coin_box_group)

    def adjust_mushroom_for_collision_x(self, item, collider):
        # changes mushroom direction if collision along x axis
        if item.rect.x < collider.rect.x:
            item.rect.right = collider.rect.x
            item.direction = c.LEFT
        else:
            item.rect.x = collider.rect.right
            item.direction = c.RIGHT

    def adjust_mushroom_for_collision_y(self, item, collider):
        # changes mushroom state to SLIDE after hitting ground from fall
        item.rect.bottom = collider.rect.y
        item.state = c.SLIDE
        item.y_vel = 0

    def adjust_star_position(self, star):
        # moves invincible star along x, y axes and checks for collisions
        if star.state == c.BOUNCE:
            star.rect.x += star.x_vel
            self.check_mushroom_x_collisions(star)
            star.rect.y += star.y_vel
            self.check_star_y_collisions(star)
            star.y_vel += star.gravity
            self.delete_if_off_screen(star)

    def check_star_y_collisions(self, star):
        # Invincible star collisions along y axis
        collider = pg.sprite.spritecollideany(star, self.ground_step_pipe_group)
        brick = pg.sprite.spritecollideany(star, self.brick_group)
        coin_box = pg.sprite.spritecollideany(star, self.coin_box_group)

        if collider:
            self.adjust_star_for_collision_y(star, collider)
        elif brick:
            self.adjust_star_for_collision_y(star, brick)
        elif coin_box:
            self.adjust_star_for_collision_y(star, coin_box)

    def adjust_star_for_collision_y(self, star, collider):
        # allows for a star bounce off the ground and on the bottom of a box
        if star.rect.y > collider.rect.y:
            star.rect.y = collider.rect.bottom
            star.y_vel = 0
        else:
            star.rect.bottom = collider.rect.top
            star.start_bounce(-8)

    def adjust_fireball_position(self, fireball):
        # moves fireball along the x, y axes and checks for collisions
        if fireball.state == c.FLYING:
            fireball.rect.x += fireball.x_vel
            self.check_fireball_x_collisions(fireball)
            fireball.rect.y += fireball.y_vel
            self.check_fireball_y_collisions(fireball)
        elif fireball.state == c.BOUNCING:
            fireball.rect.x += fireball.x_vel
            self.check_fireball_x_collisions(fireball)
            fireball.rect.y += fireball.y_vel
            self.check_fireball_y_collisions(fireball)
            fireball.y_vel += fireball.gravity
        self.delete_if_off_screen(fireball)

    def bounce_fireball(self, fireball):
        # simulates fireball bounce off ground
        fireball.y_vel = -8
        if fireball.direction == c.RIGHT:
            fireball.x_vel = 15
        else:
            fireball.x_vel = -15
        if fireball in self.powerup_group:
            fireball.state = c.BOUNCING

    def check_fireball_x_collisions(self, fireball):
        # Fireball collisions along x axis
        collide_group = pg.sprite.Group(self.ground_group, self.pipe_group, self.step_group,
                                        self.coin_box_group, self.brick_group)
        collider = pg.sprite.spritecollideany(fireball, collide_group)
        if collider:
            fireball.kill()
            self.sprites_about_to_die_group.add(fireball)
            fireball.explode_transition()

    def check_fireball_y_collisions(self, fireball):
        # fireball collisions along y axis
        collide_group = pg.sprite.Group(self.ground_group, self.pipe_group, self.step_group,
                                        self.coin_box_group, self.brick_group)
        collider = pg.sprite.spritecollideany(fireball, collide_group)
        enemy = pg.sprite.spritecollideany(fireball, self.enemy_group)
        shell = pg.sprite.spritecollideany(fireball, self.shell_group)
        if collider and (fireball in self.powerup_group):
            fireball.rect.bottom = collider.rect.y
            self.bounce_fireball(fireball)
        elif enemy:
            self.fireball_kill(fireball, enemy)
        elif shell:
            self.fireball_kill(fireball, shell)

    def fireball_kill(self, fireball, enemy):
        # Kills enemy if hit with fireball
        setup.SFX['kick'].play()
        self.game_info[c.SCORE] += 100
        self.moving_score_list.append(score.Score(enemy.rect.centerx - self.viewport.x, enemy.rect.y, 100))
        fireball.kill()
        enemy.kill()
        self.sprites_about_to_die_group.add(enemy, fireball)
        enemy.start_death_jump(fireball.direction)
        fireball.explode_transition()

    def check_if_falling(self, sprite, sprite_group):
        # checks if sprite should enter a falling state
        sprite.rect.y += 1
        if pg.sprite.spritecollideany(sprite, sprite_group) is None:
            if sprite.state != c.JUMP:
                sprite.state = c.FALL
        sprite.rect.y -= 1

    def delete_if_off_screen(self, enemy):
        # Removes enemy from sprite off the screen, underneath the bottom of the screen
        if enemy.rect.x < (self.viewport.x - 300):
            enemy.kill()
        elif enemy.rect.y > (self.viewport.bottom):
            enemy.kill()
        elif enemy.state == c.SHELL_SLIDE:
            if enemy.rect.x > (self.viewport.right + 500):
                enemy.kill()

    def check_for_mario_death(self):
        #Restarts the level if Mario dies
        if self.mario.rect.y > c.SCREEN_HEIGHT and not self.mario.in_castle:
            self.mario.dead = True
            self.mario.x_vel = 0
            self.state = c.FROZEN
            self.game_info[c.MARIO_DEAD] = True
        if self.mario.dead:
            self.play_death_song()

    def play_death_song(self):
        if self.death_timer == 0:
            self.death_timer = self.current_time
        elif (self.current_time - self.death_timer) > 3000:
            self.set_game_info_values()
            self.done = True

    def set_game_info_values(self):
        #sets the new game values after a player's death
        if self.game_info[c.SCORE] > self.persist[c.TOP_SCORE]:
            self.persist[c.TOP_SCORE] = self.game_info[c.SCORE]
        if self.mario.dead:
            self.persist[c.LIVES] -= 1
        if self.persist[c.LIVES] == 0:
            self.next = c.GAME_OVER
            self.game_info[c.CAMERA_START_X] = 0
        elif self.mario.dead == False:
            self.next = c.MAIN_MENU
            self.game_info[c.CAMERA_START_X] = 0
        elif self.overhead_info_display.time == 0:
            self.next = c.TIME_OUT
        else:
            if self.mario.rect.x > 3670 and self.game_info[c.CAMERA_START_X] == 0:
                self.game_info[c.CAMERA_START_X] = 3440
            self.next = c.LOAD_SCREEN

    def check_if_time_out(self):
        #Check if time is 0
        if self.overhead_info_display.time <= 0 \
                and not self.mario.dead \
                and not self.mario.in_castle:
            self.state = c.FROZEN
            self.mario.start_death_jump(self.game_info)

    def update_viewport(self):
        #changes view of camera
        third = self.viewport.x + self.viewport.w//3
        mario_center = self.mario.rect.centerx
        mario_right = self.mario.rect.right

        if self.mario.x_vel > 0 and mario_center >= third:
            mult = 0.5 if mario_right < self.viewport.centerx else 1
            new = self.viewport.x + mult * self.mario.x_vel
            highest = self.level_rect.w - self.viewport.w
            self.viewport.x = min(highest, new)

    def end_game(self):
        #End game
        if self.flag_timer == 0:
            self.flag_timer = self.current_time
        elif (self.current_time - self.flag_timer) > 2000:
            self.set_game_info_values()
            self.next = c.GAME_OVER
            self.sound_manager.stop_music()
            self.done = True

    def blit_everything(self, surface):
        #Blit all sprites to the main surface
        self.level.blit(self.background, self.viewport, self.viewport)
        if self.flag_score:
            self.flag_score.draw(self.level)
        self.powerup_group.draw(self.level)
        self.coin_group.draw(self.level)
        self.brick_group.draw(self.level)
        self.coin_box_group.draw(self.level)
        self.sprites_about_to_die_group.draw(self.level)
        self.shell_group.draw(self.level)
        #self.check_point_group.draw(self.level)
        self.brick_pieces_group.draw(self.level)
        self.flag_pole_group.draw(self.level)
        self.mario_and_enemy_group.draw(self.level)

        surface.blit(self.level, (0,0), self.viewport)
        self.overhead_info_display.draw(surface)
        for score in self.moving_score_list:
            score.draw(surface)