import sys
import getopt
import random
import pygame
import pygame.freetype

# Static variables
# Properties
BLOCK_SIZE = 10
SPEED = 15

# RGB-Colors
RED = (170, 20, 20)
GREEN = (20, 170, 20)
BLUE = (20, 20, 170)
BLACK = (0, 0, 0)
WHITE = (220, 220, 220)

# Variables initialized at runtime
# Window properties
DISPLAY_SIZE: tuple

# pygame
CLOCK: pygame.time.Clock
DISPLAY: pygame.Surface
GAME_FONT: pygame.freetype.Font

# Lists
snake_list: list
food_list: list
seq: list

high_score = -1


def init():
    global CLOCK
    global DISPLAY
    global GAME_FONT

    pygame.init()
    CLOCK = pygame.time.Clock()
    DISPLAY = pygame.display.set_mode(DISPLAY_SIZE)
    pygame.display.set_caption("Snake by anybuddy")

    try:
        GAME_FONT = pygame.freetype.Font("font.ttf", 24)
    except FileNotFoundError:
        print("Fatal Error: No Font file named 'font.ttf' found. Please put one next to this script!")
        exit(2)


def reset():
    global snake_list
    global food_list
    global seq

    food_list = []
    snake_list = []
    seq = []

    for x in range(10, DISPLAY_SIZE[0] - 20, 10):
        for y in range(10, DISPLAY_SIZE[1] - 20, 10):
            seq.append((x, y))


def paint(snake: list, food: list, points: int, draw_tooltip=False):
    # Draw background
    DISPLAY.fill(BLUE)

    # Draw Snake
    for snake_block in snake:
        pygame.draw.rect(DISPLAY, GREEN, [snake_block[0], snake_block[1], BLOCK_SIZE, BLOCK_SIZE])

    # Draw Food
    for food_block in food:
        pygame.draw.rect(DISPLAY, RED, [food_block[0], food_block[1], BLOCK_SIZE, BLOCK_SIZE])

    # Draw Scores
    # Current Points
    GAME_FONT.render_to(DISPLAY, (10, 10), "Score: " + str(points), WHITE)

    # Current high score
    offset = 140 + 12 * (len(str(high_score)) - 1)
    if high_score == -1:
        GAME_FONT.render_to(DISPLAY, (DISPLAY_SIZE[0] - offset + 12, 10), "High Score: -", WHITE)
    else:
        GAME_FONT.render_to(DISPLAY, (DISPLAY_SIZE[0] - offset, 10), "High Score: " + str(high_score), WHITE)

    # Draw Tooltip
    if draw_tooltip:
        loc = (DISPLAY_SIZE[0] // 2 - 136, 80)
        GAME_FONT.render_to(DISPLAY, (loc[0], loc[1]), "Press the arrow keys to play", WHITE)
        GAME_FONT.render_to(DISPLAY, (loc[0] + 50, loc[1] + 30), "Press 'Q' to Quit", WHITE)

    pygame.display.update()


def die(points: int):
    global high_score

    print("Info: Game Over")
    print(f"Info: You ate {points} pieces of food")

    if points > high_score:
        high_score = points


def add_food():
    local_seq = seq

    for snake_element in snake_list:
        try:
            local_seq.remove(snake_element)
        except ValueError:
            pass

    try:
        food = random.choice(local_seq)
        seq.remove(food)
        food_list.append(food)
    except IndexError:
        pass


def remove_food(food_element):
    food_list.remove(food_element)
    seq.append(food_element)


def game_loop(starting_food_amount: int, connected_edge: bool):
    # Per Game setup
    reset()

    game_stop = False
    game_over = False
    speed_modifier = 0

    snake_length = 1
    previous_snake_length = 1

    points = 0

    # Spawn location of snake
    x = DISPLAY_SIZE[0] // 2
    y = DISPLAY_SIZE[1] // 2
    snake_x = x - (x % 10)
    snake_y = y - (y % 10)

    snake_head = (snake_x, snake_y)
    snake_list.append(snake_head)

    move_direction = (0, 0)

    # add starting food
    for i in range(starting_food_amount):
        add_food()

    paint(snake_list, food_list, points, True)

    # Main game loop
    while not game_over:
        moved_this_frame = False

        # Register events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                die(snake_length - 1)
                game_over = True
                game_stop = True
            # Register key inputs
            if event.type == pygame.KEYDOWN:
                # Change Movement
                if not moved_this_frame:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if move_direction[0] != BLOCK_SIZE:
                            move_direction = (-BLOCK_SIZE, 0)
                            moved_this_frame = True
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if move_direction[0] != -BLOCK_SIZE:
                            move_direction = (BLOCK_SIZE, 0)
                            moved_this_frame = True
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        if move_direction[1] != BLOCK_SIZE:
                            move_direction = (0, -BLOCK_SIZE)
                            moved_this_frame = True
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if move_direction[1] != -BLOCK_SIZE:
                            move_direction = (0, BLOCK_SIZE)
                            moved_this_frame = True
                # Quit the game
                if event.key == pygame.K_q:
                    die(snake_length - 1)
                    game_over = True
                    game_stop = True
                # Add food manually
                # if event.key == pygame.K_a:
                #     add_food(food_list)

        # Skips loop if no input was made since the initialisation
        if move_direction == (0, 0):
            continue

        # Move
        snake_x += move_direction[0]
        snake_y += move_direction[1]

        # Check for Wall
        if connected_edge:
            if snake_x >= DISPLAY_SIZE[0] - 1:
                snake_x = 0
            elif snake_x < 0:
                snake_x = DISPLAY_SIZE[0] - 11
            elif snake_y >= DISPLAY_SIZE[1] - 1:
                snake_y = 0
            elif snake_y < 0:
                snake_y = DISPLAY_SIZE[1] - 11
        else:
            if snake_x > DISPLAY_SIZE[0] - 10 or snake_y > DISPLAY_SIZE[1] or snake_x < 0 or snake_y < 0:
                die(points)
                game_over = True

        # create new snake head
        snake_head = (snake_x, snake_y)
        snake_list.append(snake_head)

        # Tail biting
        for snake_block in snake_list[:-1]:
            if snake_block == snake_head:
                die(points)
                game_over = True

        # Try to eat
        for food_element in food_list:
            if snake_head == food_element:
                remove_food(food_element)
                add_food()
                snake_length += 1

        # Remove stale snake parts
        while len(snake_list) > snake_length:
            del snake_list[0]

        # Scaling
        points = snake_length - 1
        if not snake_length == previous_snake_length:
            if points <= 30:
                if points % 3 == 0:
                    speed_modifier += 1
                if points % 10 == 0:
                    add_food()
            if points > 30:
                if points % 25 == 0:
                    speed_modifier += 1
                if points % 30 == 0:
                    add_food()

            previous_snake_length = snake_length

        # Draw Frame
        paint(snake_list, food_list, points)

        CLOCK.tick(SPEED + speed_modifier)

    if game_stop:
        print("Info: Exiting game")
        pygame.quit()
        exit(0)


def main(argv: list):
    global DISPLAY_SIZE

    # Default values
    display_width = 600
    display_height = 600
    starting_food_amount = 1
    connected_edges = False

    # Messages
    msg_help = f'''\
    Options: 
        -h  --help                      Print this help
        -c  --controls                  Show the controls for the game
        
        -e  --connect-edges             Turn connected edges on. 
                                        (If the snake leaves on the right side it will come out on the left)
        
        Display sizes must be dividable by 10. On deviation the next smaller by 10 dividable number will be used!
        For aesthetic/consistency reasons is the display always 9x9 pixels smaller than a given value! 
        -w  --width  --display_width    Set display width  [Min: 300; default: {display_width}] 
        -h  --height --display_height   Set display height [Min: 300; default: {display_height}]
        
        -f  --starting-food             Sets the amount of food on startup [Min: 1; default: {starting_food_amount}]
                                          BE AWARE: Large amounts of food can cause higher loading times and lag,
                                                     as the game tries to minimize overlap!
        '''

    msg_minimum = f'''\
    Minimum values for arguments:
        Window size:    300x300 [default: {display_width}x{display_height}]
        Apples:         1       [default: {starting_food_amount}]
    '''

    msg_controls = '''\
    Controls:
        'Up' or 'W' to move up
        'Down' or 'S' tp move down
        'Left' or 'A' tp move left
        'Right' or 'D' tp move right
        
        'Q' to quit the game
    '''

    # Parse commandline arguments
    try:
        opts, args = getopt.getopt(argv, 'cew:h:f:', [
            "help", "controls", "connect-edges",
            "width=", "height=", "starting-food="
        ])
    except getopt.GetoptError:
        print("Fatal Error: Unknown arguments")
        print(msg_help)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "--help":
            print(msg_help)
            exit(0)
        if opt in ('-c', "--controls"):
            print(msg_controls)
            exit(0)
        if opt in ('-e', "--connect-edges"):
            connected_edges = True
            print("Info: Edges are connected")
        try:
            if opt in ('-w', "--width"):
                display_width = int(arg)
                deviation = display_width % 10
                if not deviation == 0:
                    print(f"Error: {display_width} is not dividable by 10")
                    display_width -= deviation
                if display_width < 300:
                    raise ValueError
                print(f"Info: Set display width to {str(display_width)}")
            if opt in ('-h', "--height"):
                display_height = int(arg)
                deviation = display_height % 10
                if not deviation == 0:
                    print(f"Error: {display_height} is not dividable by 10")
                    display_height -= deviation
                if display_width < 300:
                    raise ValueError
                print(f"Info: Set display height to {str(display_height)}")
            if opt in ('-f', "--starting-food"):
                starting_food_amount = int(arg)
                if display_width < 1:
                    raise ValueError
                print(f"Info: Set starting apples amount to {starting_food_amount}")
        except ValueError:
            print("Fatal Error: Illegal argument values")
            print(msg_minimum)
            exit(2)

    DISPLAY_SIZE = (-9 + display_width, - 9 + display_height)

    init()

    while True:
        print("Info: Starting new game!")
        game_loop(starting_food_amount, connected_edges)


if __name__ == '__main__':
    main(sys.argv[1:])
