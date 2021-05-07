# pi-connect-4

-=Numpy and Pygame are required for this project=-

 ```pip install numpy pygame```

We also recommend you install Unclutter on your Pi. It is a program that
hides your cursor after a few seconds of inactivity. It's not necessary,
but it will make the game look a lot nicer.

```sudo apt-get install unclutter```

To run the game with GPIO support, pass two arguments to the script:
```python3 connect-4.py <1,2> kiosk```.
The first argument, 1 or 2, is your piece (red or yellow). The second argument,
which enables kiosk mode, forces the game to run in fullscreen and enables
GPIO, which uses pin 24 as the button by default. This can be edited by changing
the constant BUTTON_PIN at the top of connect-4.py.
