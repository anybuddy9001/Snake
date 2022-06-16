# Snake by anybuddy

This is my first python project! :)

Feel free to try it out. \
If you happen to find an error or have a new idea please open an issue.

# Controls

    'Up'    or 'W' to move up
    'Down'  or 'S' to move down
    'Left'  or 'A' to move left
    'Right' or 'D' to move right
    
    'Q' to quit the game

# Commandline arguments

    usage: main.py [-h] [-c] [-e] [-W WIDTH] [-H HEIGHT] [--font_file FONT_FILE]
               [-f STARTING_FOOD] [--score_file SCORE_FILE] [-p] [-P]
    
    optional arguments:
      -h, --help            show this help message and exit

      -c, --controls        Show the controls for the game

      -e, --connect_edges   Turn connected edges on.
                            (If the snake leaves on the right side it will come out on the left)

      -W WIDTH, --width WIDTH
                            Set display width  [Min: 300; default: 600]

      -H HEIGHT, --height HEIGHT
                            Set display height  [Min: 300; default: 600]

      --font_file FONT_FILE
                            Sets the font file to be used to draw text. [default: LiberationSerif-Regular.ttf]
                            Be aware that character spacing can differ between fonts and therefore alignment issues may occur!
                            All font types are supported, but they must contain 'Serif'/'Sans'/'Mono' in their file name to be recognized as such!
                            Tested fonts:
                                'LiberationSerif-Regular.ttf', 'LiberationSans-Regular.ttf' and 'LiberationMono-Regular.ttf'.
                            Known issues:
                                Monospace: Display width below 320 causes visual errors on tooltip

      -f STARTING_FOOD, --starting_food STARTING_FOOD
                            Sets the amount of food on startup [Min: 1; default: 1

      --score_file SCORE_FILE
                            Sets the score file to be the specified file. [default: Scores.json]
                            The file has to be a json file, but the '.json' can be omitted. If the given file doesn't exist it will be created.
                            Example:
                                --score-file Scores.json
                                --score-file Scores
                                will both use (and create) Scores.json

      -p, --print_score     Prints the database entry with the current settings

      -P, --print_all_scores
                            Prints all entries from the current database