# PongAI

![Last commit](https://img.shields.io/github/last-commit/meridianpy/pongai.svg?color=green&label=Last%20commit) &nbsp;
![Pull Requests](https://img.shields.io/github/issues-pr-raw/meridianpy/pongai.svg?color=yellow&label=Pull%20requests)  &nbsp;
![Issues](https://img.shields.io/github/issues-raw/meridianpy/pongai.svg?color=red&label=Issues)

![Stars](https://img.shields.io/github/stars/meridianpy/pongai.svg?style=social) &nbsp;
![Watchers](https://img.shields.io/github/watchers/meridianpy/pongai.svg?label=Watchers&style=social) &nbsp;
![Followers](https://img.shields.io/github/followers/meridianpy.svg?label=Followers&style=social)

I created a Neural Network in Python that learns to play the first computer game ever, Pong.
I used the algorithm NEAT for this project and implemented it using [neat-python](https://github.com/CodeReclaimers/neat-python).

## Releases

I always compile the latest version available as a Windows executable file (exe).
All releases and the latest exe will be in the [releases](https://github.com/MeridianPy/PongAI/releases) of this project.


## How to use

Either you download the latest Windows executable from the [releases](https://github.com/MeridianPy/PongAI/releases)
or you download the source code and run the Python file using a Python interpreter.

* EXE
    * Simply download the file and double-click it.
    * A new command line window will open. It takes some time to start the application
    * Once the application is running, you will see two windows:
        * The command line window will contain information about the NEAT algorithm and the Neural Network
        * The game window will display the Pong game with the left paddle being the player or the computer.
          More on that under [Controls](#Controls).
        
* Python file
    * Download the source code.
    * Run the Python file using your Python interpreter.
    If you don't know, how to install it, I'd recommend you stick with the executable.
    * If anything goes wrong, make sure every folder is in the correct location. Use this repository's folder structure as reference.
    

## Controls

While playing the game, either by running the exe or the Python file, you can press following keys:
* Escape: This will pause the game. You can't close it at this point.
* Space Bar: This will switch the controls of the left player. The standard configuration is an automatic computer,
that simply follows the ball. It doesn't have an AI integrated. By pressing Space Bar you can control the left paddle with the arrow keys.


## Explanation

The left paddle is either controlled by the user or a script, that follows the ball, when it is moving towards it.

The right paddle(s) are controlled by a Neural Network. I used the NEAT algorithm for that. 

50 paddles are spawned with random stats. They will try to play the game as they should, but have no clue of what to do.
You will see random movement. The algorithm gets the best performing paddles by comparing the fitness value (bottom right)
of each Neural Network and getting the best values. The best two paddles will 'breed'.
The algorithm creates 50 new Neural Networks based on the best of the previous generation, but mutates every Network slightly.
This process continues until you will see a good paddle, that hits every ball.

I applied a break at score 10, which will start a new generation when reached. This will prevent one paddle being the 'winner',
just because no new generation can start, because it hits every ball. I did this because I wanted the paddles to think efficiently:
I deduct a small amount of the fitness or score when they move, which will hopefully encourage them to try to only move when necessary.
I haven't tested this for long enough tto confirm that this is working as intended.