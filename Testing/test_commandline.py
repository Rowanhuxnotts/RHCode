#! /usr/bin/env python
"""
Simple command line example of psychopy script
to allow use to test if psychopy is installed correctly and
checking lab code on other machines

Assuming that you have installed psychopy in a conda env w/ 
python 3.8, and appropriate dependencies, you can run this 
script from the command line

```bash
# activate conda env (at start of your session?)
conda activate psychopy

# run script
python test_commandline.py
```

ds 2025-01-26
"""
from psychopy import visual, core

win = visual.Window(size = [400,300], pos = [50,50], fullscr=False)
msg = visual.TextStim(win, text=u"\u00A1Hola mundo!")

msg.draw()
win.flip()
core.wait(1)
win.close()