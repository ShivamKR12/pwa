# /// script
# dependencies = [
#     "pygame-ce",
# ]
# ///


import pygame, sys, random

import asyncio


async def main():

    __ANDROID__ = hasattr(sys, "getandroidapilevel")
    __EMSCRIPTEN__ = hasattr(sys, "_emscripten_info")

    # The Block class is the most basic sprite in this project.
    # It inherits from pygame.sprite.Sprite, which allows it to be used inside sprite groups.
    # This class is mainly a helper so that we do not have to repeat the same code
    # for loading images and creating rectangles in the Player, Ball, and Opponent classes.
    # It simply loads an image from a file path, creates a surface from it,
    # and then creates a rectangle positioned at a given center coordinate.

    class Block(pygame.sprite.Sprite):
        def __init__(self, path, x_pos, y_pos):
            super().__init__()
            self.image = pygame.image.load(path)
            self.rect = self.image.get_rect(center=(x_pos, y_pos))

    # The Player class represents the paddle controlled by the user.
    # It inherits from Block, so it already has an image and a rectangle.
    # Beyond that, it introduces two new attributes:
    # speed, which defines how fast the paddle can move,
    # and movement, which stores the current vertical movement value.
    # Movement will be changed inside the event loop when keys are pressed or released.

    class Player(Block):
        def __init__(self, path, x_pos, y_pos, speed):
            super().__init__(path, x_pos, y_pos)
            self.speed = speed
            self.movement = 0

        # This method prevents the player from leaving the screen.
        # If the paddle goes above the top edge, we clamp it back to 0.
        # If it goes below the bottom edge, we clamp it back to screen_height.
        def screen_constrain(self):
            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= screen_height:
                self.rect.bottom = screen_height

        # The update method is automatically called when the sprite group updates.
        # Every frame, we move the paddle by the current movement value.
        # If no key is pressed, movement is zero, so the paddle does not move.
        # After moving, we apply the constraint check.
        def update(self, ball_group):
            self.rect.y += self.movement
            self.screen_constrain()

    # The Ball class is the most complex object in the game.
    # It also inherits from Block, so it has an image and rectangle.
    # It introduces horizontal and vertical speeds,
    # a reference to the paddle group so it can detect collisions,
    # and some state variables for handling scoring and countdown logic.

    class Ball(Block):
        def __init__(self, path, x_pos, y_pos, speed_x, speed_y, paddles):
            super().__init__(path, x_pos, y_pos)

            # Speed is randomized so the ball starts in a random direction.
            self.speed_x = speed_x * random.choice((-1, 1))
            self.speed_y = speed_y * random.choice((-1, 1))

            # Store a reference to the paddle group so collisions can be checked.
            self.paddles = paddles

            # active determines whether the ball is currently moving.
            # After a score, the ball becomes inactive until the countdown finishes.
            self.active = False

            # score_time stores the time when a score happened.
            self.score_time = 0

        # The update method controls the ball’s behavior every frame.
        # If the ball is active, it moves and checks collisions.
        # If it is not active, it shows a countdown.
        def update(self):
            if self.active:
                self.rect.x += self.speed_x
                self.rect.y += self.speed_y
                self.collisions()
            else:
                self.restart_counter()

        # This method handles all collision logic.
        # First it checks collision with the top and bottom of the screen.
        # Then it checks collision with paddles using spritecollide.
        def collisions(self):
            if self.rect.top <= 0 or self.rect.bottom >= screen_height:
                pygame.mixer.Sound.play(plob_sound)
                self.speed_y *= -1

            if pygame.sprite.spritecollide(self, self.paddles, False):
                pygame.mixer.Sound.play(plob_sound)
                collision_paddle = pygame.sprite.spritecollide(self, self.paddles, False)[0].rect

                # These checks determine from which side the collision happened.
                # Depending on the side, the direction of the ball is reversed accordingly.
                if abs(self.rect.right - collision_paddle.left) < 10 and self.speed_x > 0:
                    self.speed_x *= -1
                if abs(self.rect.left - collision_paddle.right) < 10 and self.speed_x < 0:
                    self.speed_x *= -1
                if abs(self.rect.top - collision_paddle.bottom) < 10 and self.speed_y < 0:
                    self.rect.top = collision_paddle.bottom
                    self.speed_y *= -1
                if abs(self.rect.bottom - collision_paddle.top) < 10 and self.speed_y > 0:
                    self.rect.bottom = collision_paddle.top
                    self.speed_y *= -1

        # This method is called when someone scores.
        # It resets the ball to the center, randomizes its direction,
        # sets it to inactive, and starts the countdown timer.
        def reset_ball(self):
            self.active = False
            self.speed_x *= random.choice((-1, 1))
            self.speed_y *= random.choice((-1, 1))
            self.score_time = pygame.time.get_ticks()
            self.rect.center = (screen_width / 2, screen_height / 2)
            pygame.mixer.Sound.play(score_sound)

        # This method handles the visual countdown after a score.
        # It calculates how much time has passed since scoring,
        # determines which number to display,
        # and activates the ball after 2.1 seconds.
        def restart_counter(self):
            current_time = pygame.time.get_ticks()
            countdown_number = 3

            if current_time - self.score_time <= 700:
                countdown_number = 3
            if 700 < current_time - self.score_time <= 1400:
                countdown_number = 2
            if 1400 < current_time - self.score_time <= 2100:
                countdown_number = 1
            if current_time - self.score_time >= 2100:
                self.active = True

            time_counter = basic_font.render(str(countdown_number), True, accent_color)
            time_counter_rect = time_counter.get_rect(center=(screen_width / 2, screen_height / 2 + 50))
            pygame.draw.rect(screen, bg_color, time_counter_rect)
            screen.blit(time_counter, time_counter_rect)

    # The Opponent class represents the AI paddle.
    # It inherits from Block and adds a speed attribute.
    # Its update method makes it follow the ball’s vertical position.
    # It also has a constrain method similar to the Player class.

    class Opponent(Block):
        def __init__(self, path, x_pos, y_pos, speed):
            super().__init__(path, x_pos, y_pos)
            self.speed = speed

        def update(self, ball_group):
            if self.rect.top < ball_group.sprite.rect.y:
                self.rect.y += self.speed
            if self.rect.bottom > ball_group.sprite.rect.y:
                self.rect.y -= self.speed
            self.constrain()

        def constrain(self):
            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= screen_height:
                self.rect.bottom = screen_height

    # The GameManager class ties everything together.
    # It does not inherit from Sprite.
    # Its job is to coordinate the ball, paddles, scoring, and drawing.
    # This centralizes game logic and keeps the main loop clean.

    class GameManager:
        def __init__(self, ball_group, paddle_group):
            self.player_score = 0
            self.opponent_score = 0
            self.ball_group = ball_group
            self.paddle_group = paddle_group

        # This method is called every frame.
        # It draws sprites, updates them, checks for scoring,
        # and renders the score.
        def run_game(self):
            self.paddle_group.draw(screen)
            self.ball_group.draw(screen)

            self.paddle_group.update(self.ball_group)
            self.ball_group.update()
            self.reset_ball()
            self.draw_score()

        # This checks if the ball left the screen.
        # If so, it increases the correct score and resets the ball.
        def reset_ball(self):
            if self.ball_group.sprite.rect.right >= screen_width:
                self.opponent_score += 1
                self.ball_group.sprite.reset_ball()
            if self.ball_group.sprite.rect.left <= 0:
                self.player_score += 1
                self.ball_group.sprite.reset_ball()

        # This renders both scores and places them around the center line.
        def draw_score(self):
            player_score = basic_font.render(str(self.player_score), True, accent_color)
            opponent_score = basic_font.render(str(self.opponent_score), True, accent_color)

            player_score_rect = player_score.get_rect(midleft=(screen_width / 2 + 40, screen_height / 2))
            opponent_score_rect = opponent_score.get_rect(midright=(screen_width / 2 - 40, screen_height / 2))

            screen.blit(player_score, player_score_rect)
            screen.blit(opponent_score, opponent_score_rect)

    # The rest of the code below handles initialization,
    # window setup, global variables, object creation,
    # and the main game loop. The main loop is now very clean
    # because most logic has been moved into classes.

    # Increase the audio buffer size to 1024 (from 512).
    # A larger buffer gives mobile browsers more time to process audio without crackling.
    pygame.mixer.pre_init(44100, -16, 2, 1024)
    pygame.init()
    clock = pygame.time.Clock()

    screen_width = 1300
    screen_height = 650

    if __ANDROID__:
        screen = pygame.display.set_mode((screen_width, screen_height),
                                        pygame.SCALED | pygame.FULLSCREEN)
    elif __EMSCRIPTEN__:
        screen = pygame.display.set_mode((screen_width, screen_height), 0)
    else:
        screen = pygame.display.set_mode((screen_width, screen_height),
                                        pygame.SCALED | pygame.RESIZABLE)
    
    pygame.display.set_caption("Pong")
    pygame.display.set_icon(pygame.image.load("favicon.png"))

    bg_color = pygame.Color("#2F373F")
    accent_color = (27, 35, 43)
    basic_font = pygame.font.Font("freesansbold.ttf", 32)
    plob_sound = pygame.mixer.Sound("assets/pong.ogg")
    score_sound = pygame.mixer.Sound("assets/score.ogg")
    middle_strip = pygame.Rect(screen_width / 2 - 2, 0, 4, screen_height)

    player = Player("assets/Paddle.png", screen_width - 20, screen_height / 2, 5)
    opponent = Opponent("assets/Paddle.png", 20, screen_width / 2, 5)

    paddle_group = pygame.sprite.Group()
    paddle_group.add(player)
    paddle_group.add(opponent)

    ball = Ball("assets/Ball.png", screen_width / 2, screen_height / 2, 4, 4, paddle_group)
    ball_sprite = pygame.sprite.GroupSingle()
    ball_sprite.add(ball)

    game_manager = GameManager(ball_sprite, paddle_group)

    fingers = {}

    while True:
        pygame.event.pump()
        for event in pygame.event.get(pygame.QUIT, pump=False):
            pygame.quit()
            sys.exit()
        for event in pygame.event.get(pygame.KEYDOWN, pump=False):
            if event.key == pygame.K_UP:
                player.movement -= player.speed
            if event.key == pygame.K_DOWN:
                player.movement += player.speed
        for event in pygame.event.get(pygame.KEYUP, pump=False):
            if event.key == pygame.K_UP:
                player.movement += player.speed
            if event.key == pygame.K_DOWN:
                player.movement -= player.speed
        for event in pygame.event.get(pygame.FINGERDOWN, pump=False):
            x = event.x * screen.get_width()
            y = event.y * screen.get_height()
            fingers[event.finger_id] = (x, y)
        for event in pygame.event.get(pygame.FINGERMOTION, pump=False):
            x = event.x * screen.get_width()
            y = event.y * screen.get_height()
            fingers[event.finger_id] = (x, y)
        for event in pygame.event.get(pygame.FINGERUP, pump=False):
            fingers.pop(event.finger_id, None)

        if fingers:
            finger_id = list(fingers.keys())[0]
            _, fy = fingers[finger_id]
            player.rect.centery = int(fy)
            player.screen_constrain()

        screen.fill(bg_color)
        pygame.draw.rect(screen, accent_color, middle_strip)

        game_manager.run_game()

        pygame.display.flip()

        # Yield control to the browser. This natively syncs with the screen's refresh rate.
        await asyncio.sleep(0)

        # Do not hard-cap the framerate! It fights the browser and causes audio buffer starvation.
        # To keep game speed consistent across monitors, you'll eventually want to use delta time.
        clock.tick()


asyncio.run(main())
