# pi-connect-4
-=Group Members=-
Brendan Guillory
Austin Hampton
Chris Clent
Zak Kilpatrick


-=Numpy and Pygame are required for this project=-

 ```pip install numpy pygame```

We also recommend you install Unclutter on your Pi. It is a program that
hides your cursor after a few seconds of inactivity. It's not necessary,
but it will make the game look a lot nicer. ```sudo apt-get install unclutter```

-=Running the Game=-

To play the game without GPIO support or full-screen, simply run connect-4.py
and pass a 1 or 2 to indicate whether you'd like to be red or yellow. Another
computer must be running the server.py file, and the clients look for the server
based on the values of SERVER_IP and PORT in connect-4.py.

To run the game with GPIO support, pass two arguments to the script:
```python3 connect-4.py <1,2> kiosk```.
The first argument, 1 or 2, is your piece (red or yellow). The second argument,
which enables kiosk mode, forces the game to run in full-screen and enables
GPIO.

By default, the button is wired between +5V and pin 24. The LED is wired from
pin 23 to GND. Both of these pins are constants in connect-4.py. Diagrams of
these connections can be found in the Diagrams folder.
