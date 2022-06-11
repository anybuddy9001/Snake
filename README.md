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

    Usage: python main.py [Options]

    Options: 
        -h  --help                      Print this help
        -c  --controls                  Show the controls for the game
                                                
        --score-file                    Sets the score file to be the specified file. [default: Scores.json]
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
        -w  --width  --display_width    Set display width  [Min: 300; default: 600] 
        -h  --height --display_height   Set display height [Min: 300; default: 600]
        
        --font-file                     Sets the font file to be used to draw text. Be aware that character spacing can
                                        differ between fonts and therefore alignment issues may occur!
                                        SansSerif and Monospace fonts are supported as well, but they must contain 
                                        'Mono'/'Sans' in their file name to be recognized as such!
                                        Tested fonts: 'LiberationSerif-Regular.ttf', 'LiberationSans-Regular.ttf' and 
                                        'LiberationMono-Regular.ttf'. [Default: LiberationSerif-Regular.ttf]
                                        Known issues: 
                                            Monospace: Display width below 330 causes tooltip to glitch
        
        -f  --starting-food             Sets the amount of food on startup [Min: 1; default: 1]

        Print scores:                               
        -p --print-scores               Prints the database entry with the current settings
        -P --print-all-scores           Prints all entries from the current database