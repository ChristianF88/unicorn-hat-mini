# Unicorn-Hat-Mini Games

This repo contains some basic games for the unicorn hat mini.
- The app contains a menu buttons pressed are registered at the main app level and passed to the menu and the running games.
- A reaction game with different levels of difficulty
- Mazes to be solved with different levels of difficulty
- A space shooter with two difficulty levels
- Conway's Game of Life with a cell editor and simulation mode
- Some other demos and test
- Animations during games

Some important button combinations:

In Menu:
*A - enter*
*B - back*
*X - up*
*Y - down*

In Games:
Depends on the game, but in every Game -> **_Long press A+B+X+Y_ - Exit Game**

For the installation see the `install.sh`.

The app is tested on an old version of Raspbian on a Raspberry Pi ZW.

It would not be hard to change the menu and add new games.
Check out the tests to get a better idea how it works.

## Optimized unicornhatmini library

This project uses an optimized version of the Pimoroni unicornhatmini driver
bundled in `unicornhatmini-fast/`. It is a drop-in replacement with the same
API, but uses numpy-accelerated bulk operations and `writebytes2` for
significantly faster rendering on the RPi Zero W.

To install:

```bash
pip uninstall unicornhatmini
pip install -e unicornhatmini-fast/
```

See `unicornhatmini-fast/CHANGELOG.md` for details on what was optimized
and why.
