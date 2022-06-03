import sys
import getopt
import pygame
import pygame.freetype
import random

# Window properties
display_width = 600
display_height = 600
display_size = None

GAME_FONT = None

# Snake properties
snake_size = 10
snake_speed = 15

high_score = -1

# RGB-Colors
red = (170, 20, 20)
green = (20, 170, 20)
blue = (20, 20, 170)
black = (0, 0, 0)
white = (220, 220, 220)

clock = None

display = None


def init():
    global clock
    global display
    global GAME_FONT

    pygame.init()
    clock = pygame.time.Clock()
    display = pygame.display.set_mode(display_size)
    pygame.display.set_caption("Snake by anybuddy")

    try:
        GAME_FONT = pygame.freetype.Font("font.ttf", 24)
    except FileNotFoundError:
        print("No Font file named 'font.ttf' found. Please put one next to this script!")
        exit(2)


# noinspection PyUnresolvedReferences,PyTypeChecker
def paint(snake, food, points, draw_tooltip=False):
    # Draw background
    display.fill(blue)

    # Draw Snake
    for snake_block in snake:
        pygame.draw.rect(display, green, [snake_block[0], snake_block[1], snake_size, snake_size])

    # Draw Food
    for food_block in food:
        pygame.draw.rect(display, red, [food_block[0], food_block[1], snake_size, snake_size])

    # Draw Scores
    # Current Points
    GAME_FONT.render_to(display, (10, 10), "Score: " + str(points), white)

    # Current high score
    offset = 140 + 12 * (len(str(high_score)) - 1)
    if high_score == -1:
        GAME_FONT.render_to(display, (display_size[0] - offset + 12, 10), "High Score: -", white)
    else:
        GAME_FONT.render_to(display, (display_size[0] - offset, 10), "High Score: " + str(high_score), white)

    # Draw Tooltip
    if draw_tooltip:
        loc = (display_size[0] // 4, 80)
        GAME_FONT.render_to(display, (loc[0], loc[1]), "Press the arrow keys to play", white)
        GAME_FONT.render_to(display, (loc[0] + 50, loc[1] + 30), "Press 'Q' to Quit", white)

    pygame.display.update()


def die(snake_length):
    global high_score
    points = snake_length - 1
    print("Game Over")
    print("You ate", points, "pieces of food")

    if points > high_score:
        high_score = points


# noinspection PyUnresolvedReferences
def add_food(food_list):
    food_x = random.randint(50, display_size[0] - 20)
    food_y = random.randint(50, display_size[1] - 20)
    food_list.append((food_x, food_y))


# noinspection PyUnresolvedReferences
def game_loop():
    game_stop = False
    game_over = False
    speed_modifier = 0

    snake_list = []
    snake_length = 1
    previous_snake_length = 1

    points = 0

    snake_x = display_size[0] // 2
    snake_y = display_size[1] // 2

    snake_head = (snake_x, snake_y)
    snake_list.append(snake_head)

    x_direction = 0
    y_direction = 0

    food_list = []
    add_food(food_list)

    paint(snake_list, food_list, points, True)

    while not game_over:
        # Register key inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                die(snake_length)
                game_over = True
                game_stop = True

            if event.type == pygame.KEYDOWN:
                # Change Movement
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if x_direction != snake_size:
                        x_direction = -snake_size
                        y_direction = 0
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if x_direction != -snake_size:
                        x_direction = snake_size
                        y_direction = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    if y_direction != snake_size:
                        x_direction = 0
                        y_direction = -snake_size
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if y_direction != -snake_size:
                        x_direction = 0
                        y_direction = snake_size
                # Quit the game
                if event.key == pygame.K_q:
                    die(snake_length)
                    game_over = True
                    game_stop = True

                # Add food manually
                # if event.key == pygame.K_a:
                #     add_food(food_list)

        # Skip loop if no input was made
        if x_direction == 0 and y_direction == 0:
            continue

        # Move
        snake_x += x_direction
        snake_y += y_direction

        snake_head = (snake_x, snake_y)
        snake_list.append(snake_head)

        # Remove stale snake parts
        if len(snake_list) > snake_length:
            del snake_list[0]

        # Try to eat
        for food_element in food_list:
            if abs(food_element[0] - snake_head[0]) <= 10 and abs(food_element[1] - snake_head[1]) <= 10:
                food_list.remove(food_element)
                add_food(food_list)
                snake_length += 1

        # Check for Death
        # Wall
        if snake_x > display_size[0] - 10 or snake_y > display_size[1] or snake_x < 0 or snake_y < 0:
            die(snake_length)
            game_over = True
        # Tail biting
        for x in snake_list[:-1]:
            if x == snake_head:
                die(snake_length)
                game_over = True

        # Scaling
        points = snake_length - 1
        if not snake_length == previous_snake_length:
            if points <= 30:
                if points % 3 == 0:
                    speed_modifier += 1
                if points % 10 == 0:
                    add_food(food_list)
            if points > 30:
                if points % 25 == 0:
                    speed_modifier += 1
                if points % 30 == 0:
                    add_food(food_list)

            previous_snake_length = snake_length

        # Next Frame
        paint(snake_list, food_list, points)

        clock.tick(snake_speed + speed_modifier)

    if game_stop:
        print("Exiting game")
        pygame.quit()
        exit(0)


def main(argv):
    global display_width
    global display_height
    global display_size

    msg_help = '''\
    Options: 
        -h --help                       Print this help
        -c --controls                   Show the controls for the game
        -dw --display_width --width     Set display width [default: {display_width}] 
        -dh --display_height --height   Set display height [default: {display_height}]
        '''.format(display_width=display_width, display_height=display_height)
    msg_controls = '''\
    Controls:
        'Up' or 'W' to move up
        'Down' or 'S' tp move down
        'Left' or 'A' tp move left
        'Right' or 'D' tp move right
        
        'Q' to quit the game
    '''

    try:
        opts, args = getopt.getopt(argv, 'cw:h:',
                                   ["help", "controls", "display_width=", "width=", "display_height=", "height="])
    except getopt.GetoptError:
        print("Error: Unknown arguments")
        print(msg_help)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "--help":
            print(msg_help)
            exit(0)
        if opt in ('-c', "--controls"):
            print(msg_controls)
            exit(0)
        if opt in ('-w', "--width", "--display_width"):
            display_width = int(arg)
            print("Set display width to " + str(display_width))
        if opt in ('-h', "--height", "--display_height"):
            display_height = int(arg)
            print("Set display height to " + str(display_height))

    display_size = (display_width, display_height)

    init()

    while True:
        print("Starting new game!")
        game_loop()


if __name__ == '__main__':
    main(sys.argv[1:])
