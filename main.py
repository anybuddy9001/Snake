import sys
import getopt
import random
import pygame
import pygame.freetype

# Window properties
display_width = 600
display_height = 600
display_size = None

# Snake properties
snake_size = 10
snake_speed = 15

# Lists
snake_list = []
food_list = []

high_score = -1

# RGB-Colors
red = (170, 20, 20)
green = (20, 170, 20)
blue = (20, 20, 170)
black = (0, 0, 0)
white = (220, 220, 220)

clock = None
display = None
GAME_FONT = None


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


def reset():
    global snake_list
    global food_list

    food_list = []
    snake_list = []


# noinspection PyUnresolvedReferences,PyTypeChecker
def paint(snake: list, food: list, points: int, draw_tooltip=False):
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


def die(points: int):
    global high_score

    print("Game Over")
    print(f"You ate {points} pieces of food")

    if points > high_score:
        high_score = points


# noinspection PyUnresolvedReferences
def add_food():
    global food_list

    food_x = random.randint(50, display_size[0] - 20)
    food_y = random.randint(50, display_size[1] - 20)
    food_list.append((food_x, food_y))


# noinspection PyUnresolvedReferences
def game_loop(starting_food_amount: int, connected_edge: bool):
    # Per Game setup
    game_stop = False
    game_over = False
    speed_modifier = 0
    reset()

    snake_length = 1
    previous_snake_length = 1

    points = 0

    snake_x = display_size[0] // 2
    snake_y = display_size[1] // 2

    snake_head = (snake_x, snake_y)
    snake_list.append(snake_head)

    move_direction = (0, 0)

    # add starting food
    if starting_food_amount > 0:
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
                        if move_direction[0] != snake_size:
                            move_direction = (-snake_size, 0)
                            moved_this_frame = True
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if move_direction[0] != -snake_size:
                            move_direction = (snake_size, 0)
                            moved_this_frame = True
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        if move_direction[1] != snake_size:
                            move_direction = (0, -snake_size)
                            moved_this_frame = True
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if move_direction[1] != -snake_size:
                            move_direction = (0, snake_size)
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
            if snake_x > display_size[0] - 10:
                snake_x = 0
            elif snake_x < 0:
                snake_x = display_size[0]
            elif snake_y > display_size[1] - 10:
                snake_y = 0
            elif snake_y < 0:
                snake_y = display_size[1]
        else:
            if snake_x > display_size[0] - 10 or snake_y > display_size[1] or snake_x < 0 or snake_y < 0:
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

        # Remove stale snake parts
        if len(snake_list) > snake_length:
            del snake_list[0]

        # Try to eat
        for food_element in food_list:
            if abs(food_element[0] - snake_head[0]) <= 10 and abs(food_element[1] - snake_head[1]) <= 10:
                food_list.remove(food_element)
                add_food()
                snake_length += 1

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

        clock.tick(snake_speed + speed_modifier)

    if game_stop:
        print("Exiting game")
        pygame.quit()
        exit(0)


def main(argv: list):
    global display_width
    global display_height
    global display_size

    # Default values
    starting_food_amount = 1
    connected_edges = True

    # Messages
    msg_help = f'''\
    Options: 
        -h  --help                      Print this help
        -c  --controls                  Show the controls for the game
        -e  --connect-edges             Toggle connected edges [default: {connected_edges}]
        -w  --width  --display_width    Set display width  [Min: 300; default: {display_width}] 
        -h  --height --display_height   Set display height [Min: 300; default: {display_height}]
        -f  --starting-food             Sets the amount of food on startup [Min: 1; default: {starting_food_amount}]
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
        if opt in ('-e', "--connect-edges"):
            connected_edges = not connected_edges
        try:
            if opt in ('-w', "--width"):
                display_width = int(arg)
                if display_width < 300:
                    raise ValueError
                print(f"Set display width to {str(display_width)}")
            if opt in ('-h', "--height"):
                display_height = int(arg)
                if display_width < 300:
                    raise ValueError
                print(f"Set display height to {str(display_height)}")
            if opt in ('-f', "--starting-food"):
                starting_food_amount = int(arg)
                if display_width < 1:
                    raise ValueError
        except ValueError:
            print("Error: Illegal values")
            print(msg_minimum)
            exit(2)

    display_size = (display_width, display_height)

    init()

    while True:
        print("Starting new game!")
        game_loop(starting_food_amount, connected_edges)


if __name__ == '__main__':
    main(sys.argv[1:])
