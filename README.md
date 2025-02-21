# haptic-reconfiguration

This is the repo for the Mechanical and Algorithmic Reconfiguration of Soft Haptics

## For Antonio:
`main.py` script has instructions and can be used with joystick inputs to record robot data.

Test the following:
- Potential typos/bugs
- Check target point generation
- Test main.py iterations
- Check file saving/loading


## For Soheil:
We need:
- :white_check_mark: A script structure that allow a user to move the robot to find target positions.
- :white_check_mark: The target positions are predetermined from a list, and are likely defined as (x,y) coords, but (x,y,z) works as well.
- :white_check_mark: The user would start from the home position (we can redefine home later). When the "game" starts, the robot is backdrivable and the user moves.
- :white_check_mark: A script generating random target points in a controlled way
- :white_check_mark: `main.py` updated to iterate over target points and compute euclidean distance without z
- :white_check_mark: `main.py` prints in terminal when user reached the target
- We then grab the position of the end effector in real time to calculation euclidean distance to the target. Based on this distance, we send information to an Arduino controlling the pneumatics.
- One the user finds the target, we need to have an alert or indication of some sort that the trial has been completed. I could just tell them "you found the target," or maybe have a buzzer or whatever. Can we stop the robot from moving once the target is found?
- After this, the robot goes back to home and we continue with the next target.

Information we need to collect for each trial:
-  Coordinates in real time
-  Target coordinates. Home/start coordinates
-  Time
-  Whatever we send to the Arduino
-  Arduino data (we'll deal with this later)

Stuff that would be nice to do but don't know if it is possible:
- Restrict robot motion to a single plane. Would it make it harder for the user to move the robot? Maybe not even possible.
