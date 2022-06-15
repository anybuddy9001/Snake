import sys
import getopt
import random
from enum import Enum
import json

import pygame
import pygame.freetype

# Static variables
# Properties
BLOCK_SIZE = 10
SPEED = 15


# Enums
class Color(Enum):
    RED = (170, 20, 20)
    GREEN = (20, 170, 20)
    BLUE = (20, 20, 170)
    BLACK = (0, 0, 0)
    WHITE = (220, 220, 220)


class FontType(Enum):
    Serif = 24
    SansSerif = 21
    Monospace = 20


# Variables initialized at runtime
# Window properties
DISPLAY_SIZE: tuple
STARTING_FOOD_AMOUNT: int
CONNECTED_EDGES: bool

# File references
SCORE_FILE: str
SESSION_ID: int

# pygame
CLOCK: pygame.time.Clock
DISPLAY: pygame.Surface
GAME_FONT: pygame.freetype.Font
FONT_TYPE: FontType

# Lists
snake_list: list
food_list: list
seq: list

high_score: int


def init(font_file):
    global CLOCK
    global DISPLAY
    global GAME_FONT

    pygame.init()

    try:
        GAME_FONT = pygame.freetype.Font(font_file, FONT_TYPE.value)
    except FileNotFoundError:
        print(f'''Fatal Error: '{font_file}' is non-existent or not a font file.
                               Please put a valid font file named 'font.ttf next to this script or 
                               use '--font-file' to point to valid one!
        ''')
        exit(2)

    CLOCK = pygame.time.Clock()
    DISPLAY = pygame.display.set_mode(DISPLAY_SIZE)
    pygame.display.set_caption("Snake by anybuddy")


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


def get_element_index(data) -> int:
    for element in data:
        if element["display_size"] == str((DISPLAY_SIZE[0], DISPLAY_SIZE[1])):
            if element["connected_edges"] == int(CONNECTED_EDGES):
                if element["starting_food_amount"] == STARTING_FOOD_AMOUNT:
                    return data.index(element)
    return -1


def get_high_score():
    global high_score
    global SESSION_ID

    new_entry = ('{'
                 f'"display_size" : "{(DISPLAY_SIZE[0], DISPLAY_SIZE[1])}", '
                 f'"connected_edges" : {int(CONNECTED_EDGES)}, '
                 f'"starting_food_amount" : {STARTING_FOOD_AMOUNT}, '
                 '"high_score" : -1'
                 '}')

    try:
        with open(SCORE_FILE) as fin:
            data = json.load(fin)

        # Check if `SESSION_ID` has been initialised and the session is in save file
        try:
            if SESSION_ID == -1:
                raise NameError
        except NameError:
            SESSION_ID = get_element_index(data)

        if SESSION_ID == -1:
            data.append(json.loads(new_entry))
            with open(SCORE_FILE, 'w') as fout:
                json.dump(data, fout, indent=4, ensure_ascii=False)
            high_score = -1
        else:
            high_score = data[SESSION_ID]["high_score"]

    except FileNotFoundError:
        # Create a new file from scratch
        with open(SCORE_FILE, 'w') as fout:
            starting_entry = '[' + new_entry + ']'
            data = json.loads(starting_entry)
            json.dump(data, fout, indent=4, ensure_ascii=False)
        # Initialize runtime variables
        high_score = -1
        SESSION_ID = 0


def set_high_score(new_score: int):
    if high_score < new_score:
        with open(SCORE_FILE, 'r') as fin:
            data = json.load(fin)

        data[SESSION_ID]["high_score"] = new_score

        with open(SCORE_FILE, 'w') as fout:
            json.dump(data, fout, indent=4, ensure_ascii=False)


def paint(points: int, draw_tooltip=False):
    # Draw background
    DISPLAY.fill(Color.BLUE.value)

    # Draw Snake
    for snake_block in snake_list:
        pygame.draw.rect(DISPLAY, Color.GREEN.value, [snake_block[0], snake_block[1], BLOCK_SIZE, BLOCK_SIZE])

    # Draw Food
    for food_block in food_list:
        pygame.draw.rect(DISPLAY, Color.RED.value, [food_block[0], food_block[1], BLOCK_SIZE, BLOCK_SIZE])

    # Draw Scores
    off = 140 + 12 * (len(str(high_score)) - 1)  # High score offset from the display edge
    loc = (DISPLAY_SIZE[0] // 2 - 136, 80)  # Location of the first tooltip line
    loc_off = 55  # Location offset of the second tooltip line

    if FONT_TYPE is FontType.SansSerif:
        off -= 7
        loc = (loc[0] + 2, loc[1])
        # loc_off needs no change
    elif FONT_TYPE is FontType.Monospace:
        off += 25
        loc = (loc[0] - 30, loc[1])
        loc_off += 12

    # Current Points
    GAME_FONT.render_to(DISPLAY, (10, 10), "Score: " + str(points), Color.WHITE.value)

    # Current high score
    if high_score == -1:
        GAME_FONT.render_to(DISPLAY, (DISPLAY_SIZE[0] - off + 12, 10), "High Score: -", Color.WHITE.value)
    else:
        GAME_FONT.render_to(DISPLAY, (DISPLAY_SIZE[0] - off, 10), "High Score: " + str(high_score), Color.WHITE.value)

    # Draw Tooltip
    if draw_tooltip:
        GAME_FONT.render_to(DISPLAY, (loc[0], loc[1]), "Press the arrow keys to play", Color.WHITE.value)
        GAME_FONT.render_to(DISPLAY, (loc[0] + loc_off, loc[1] + 30), "Press 'Q' to Quit", Color.WHITE.value)

    pygame.display.update()


def die(points: int):
    print("Info: Game Over")
    print(f"Info: You ate {points} pieces of food")

    set_high_score(points)


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


def game_loop():
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
    for i in range(STARTING_FOOD_AMOUNT):
        add_food()

    get_high_score()

    paint(points, True)

    # Main game loop
    while not game_over:
        moved_this_frame = False

        # Register events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                die(points)
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
                    die(points)
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
        if CONNECTED_EDGES:
            if snake_x >= DISPLAY_SIZE[0]:
                snake_x = 0
            elif snake_x < 0:
                snake_x = DISPLAY_SIZE[0] - 10
            elif snake_y >= DISPLAY_SIZE[1]:
                snake_y = 0
            elif snake_y < 0:
                snake_y = DISPLAY_SIZE[1] - 10
        else:
            if snake_x >= DISPLAY_SIZE[0] or snake_y >= DISPLAY_SIZE[1] or snake_x < 0 or snake_y < 0:
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
        paint(points)

        CLOCK.tick(SPEED + speed_modifier)

    if game_stop:
        print("Info: Exiting game")
        pygame.quit()
        exit(0)


def print_scores(full=False):
    try:
        with open(SCORE_FILE) as fin:
            data = json.load(fin)

        print(f"Found {len(data)} entries in `{SCORE_FILE}`")

        if full:
            for block in data:
                print(f"Entry {data.index(block) + 1}:\n"
                      f"    High Score: {block['high_score']}\n"
                      f"    Display: {block['display_size']}\n"
                      f"    Connected Edges: {bool(block['connected_edges'])}\n"
                      f"    Starting Food Amount: {block['starting_food_amount']}"
                      )
        else:
            get_high_score()
            block = data[SESSION_ID]
            print(f"Entry {data.index(block) + 1}:\n"
                  f"    High Score: {block['high_score']}\n"
                  f"    Display: {block['display_size']}\n"
                  f"    Connected Edges: {bool(block['connected_edges'])}\n"
                  f"    Starting Food Amount: {block['starting_food_amount']}"
                  )
    except OSError:
        print(f"Fatal: Could not open '{SCORE_FILE}'. Maybe it doesn't exist?")
        exit(2)


def main(argv: list):
    global DISPLAY_SIZE
    global CONNECTED_EDGES
    global STARTING_FOOD_AMOUNT
    global FONT_TYPE
    global SCORE_FILE

    # Default values
    SCORE_FILE = "Scores.json"

    display_width = 600
    display_height = 600
    CONNECTED_EDGES = False
    STARTING_FOOD_AMOUNT = 1

    font_file = "LiberationSerif-Regular.ttf"
    FONT_TYPE = FontType.Serif

    do_print_scores = False
    full = False

    # Messages
    msg_help = f'''\
    Usage: python main.py [Options] [-Pp]

    Options: 
        -h  --help                      Print this help
        -c  --controls                  Show the controls for the game
                                                
        --score-file                    Sets the score file to be the specified file. [default: {SCORE_FILE}]
                                        The file has to be a json file, but the '.json' can be omitted.
                                        If the given file doesn't exist it will be created.
                                        Example:
                                            --score-file Scores.json
                                            --score-file Scores
                                            will both use (and create) Scores.json
                                            
        
        -e  --connect-edges             Turn connected edges on. 
                                        (If the snake leaves on the right side it will come out on the left)
        
        Display sizes must be dividable by 10. On deviation the next smaller by 10 dividable number will be used!
        For aesthetic/consistency reasons is the display always 9x9 pixels smaller than a given value! 
        -w  --width  --display_width    Set display width  [Min: 300; default: {display_width}] 
        -h  --height --display_height   Set display height [Min: 300; default: {display_height}]
        
        --font-file                     Sets the font file to be used to draw text. Be aware that character spacing can
                                        differ between fonts and therefore alignment issues may occur!
                                        SansSerif and Monospace fonts are supported as well, but they must contain 
                                        'Mono'/'Sans' in their file name to be recognized as such!
                                        Tested fonts: 'LiberationSerif-Regular.ttf', 'LiberationSans-Regular.ttf' and 
                                        'LiberationMono-Regular.ttf'. [Default: {font_file}]
                                        Known issues: 
                                            Monospace: Display width below 330 causes tooltip to glitch
        
        -f  --starting-food             Sets the amount of food on startup [Min: 1; default: {STARTING_FOOD_AMOUNT}]

        Print scores:                               
        -p --print-scores               Prints the database entry with the current settings
        -P --print-all-scores           Prints all entries from the current database
        '''

    msg_minimum = f'''\
    Minimum values for arguments:
        Window size:    300x300 [default: {display_width}x{display_height}]
        Apples:         1       [default: {STARTING_FOOD_AMOUNT}]
    '''

    msg_controls = '''\
    Controls:
        'Up' or 'W' to move up
        'Down' or 'S' to move down
        'Left' or 'A' to move left
        'Right' or 'D' to move right
        
        'Q' to quit the game
    '''

    # Parse commandline arguments
    try:
        opts, args = getopt.getopt(argv, 'cew:h:f:pP',
                                   [
                                       "help", "controls", "connect-edges",
                                       "width=", "height=", "starting-food=",
                                       "font-file=", "score-file=", "print-scores", "print-all-scores"
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
            CONNECTED_EDGES = True
            print("Info: Edges are connected")
        if opt == "--font-file":
            font_file = arg
            if not font_file[-4:] == '.ttf':
                print(f"Fatal Error: {font_file} is not a font file! Required Suffix: '.ttf'")
                exit(2)
            if not font_file.rfind("Sans") == -1:
                FONT_TYPE = FontType.SansSerif
            if not font_file.rfind("Mono") == -1:
                FONT_TYPE = FontType.Monospace
                if display_width < 330:
                    print("Critical: Display width below 330 causes tooltip to glitch")
            print(f"Info: Set font to '{font_file}' of type {FONT_TYPE.name}")
        if opt == "--score-file":
            new_file = arg
            if new_file.endswith('.json'):
                SCORE_FILE = new_file
            elif not ('.' in new_file):
                SCORE_FILE = new_file + '.json'
            else:
                print(f"Fatal: '{new_file}' is not a json file and/or has a different suffix!")
                exit(2)
            print(f"Info: Set score file to '{SCORE_FILE}'")
        if opt in ('-p', "--print-scores"):
            do_print_scores = True
        if opt in ('-P', "--print-all-scores"):
            do_print_scores = True
            full = True
        # Catch ValueErrors
        try:
            if opt in ('-w', "--width"):
                display_width = int(arg)
                deviation = display_width % 10
                if not deviation == 0:
                    print(f"Error: '{display_width}' is not a multiple of 10")
                    display_width -= deviation
                if display_width < 300:
                    raise ValueError
                print(f"Info: Set display width to '{str(display_width)}'")
            if opt in ('-h', "--height"):
                display_height = int(arg)
                deviation = display_height % 10
                if not deviation == 0:
                    print(f"Error: '{display_height}' is not a multiple of 10")
                    display_height -= deviation
                if display_width < 300:
                    raise ValueError
                print(f"Info: Set display height to '{str(display_height)}'")
            if opt in ('-f', "--starting-food"):
                STARTING_FOOD_AMOUNT = int(arg)
                if display_width < 1:
                    raise ValueError
                print(f"Info: Set starting apples amount to '{STARTING_FOOD_AMOUNT}'")
        except ValueError:
            print("Fatal Error: Illegal argument values")
            print(msg_minimum)
            exit(2)

    DISPLAY_SIZE = (display_width, display_height)

    if do_print_scores:
        if full:
            print_scores(True)
        else:
            print_scores()
        exit(0)

    init(font_file)

    while True:
        print("Info: Starting new game!")
        game_loop()


if __name__ == '__main__':
    main(sys.argv[1:])
