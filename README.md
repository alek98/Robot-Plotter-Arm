# Robot Plotter Arm project

### The goal of this python project was to make a plotter which can draw lines, shapes and images. It is cheap, simple and easy to build. The focus isn't on a hardware itself, but on a software.
#
#


(add the image)
#### Hardware components:
 - Raspberry Pi 3
 - one stepper motor
 - one servo motor
 - two arms
 - GPIO pins


#
#
#
##### There is also a software simulation, where actual hardware parts aren't necessary. 
The main entry point is file rpi_app2.py. 
If hardware parts are connected, software should start moving motors and draw the image. If hardware aren't connected software should start drawing simulation. Here is the picture of software simulation.
(add the image)

***
Before drawing you need:
- StepperMotor object and ServoMotor object initialized
    - they execute the motor movement 
- Boundaries object 
    - is a boxed-shaped space which a pen for drawing can reach
    - params are 4 coordintes in meased in cm: left_down_corner, right_down_corner, left_up_corner, right_up_corner
- Pen object
    - is representing a pen, having some params like arm length
    - it gives instructions to stepper & servo motor to move
- Photo object
    -  takes photo name as a parameter
    
When all of the above mentioned is fulfilled, you can call methods for drawing photos (one of the following methods)
```
draw_photo1(photo)
draw_photo2(photo)
```

Here is an example:
```
stepper = StepperMotor()
servo = ServoMotor()

boundaries = Boundaries(
    left_down_corner= (-4.7, 5.85),
    right_down_corner = (4.7, 5.85),
    left_up_corner= (-4.7, 15.35),
    right_up_corner=(4.7, 15.35)
)
pen = Pen()
photo = Photo('star')
draw_photo2(photo)
```

***
For more detailed documentation check out:
https://github.com/alek98/Robot-Plotter-Arm/tree/master/documentation



