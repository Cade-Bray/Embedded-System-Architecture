This entry is lab notes on how the process of the pulse width modulation lab went. The lab guide can be found at [[CS 350 Milestone One PMW Lab Guide.pdf]].

#### Milestone Objectives
- Develop **code** for all the specified **functionality** of the PWM peripheral outlined in the Milestone One PWM Lab Guide.
- Discuss the **questions** from the Milestone One PWM Lab Guide.
- Apply coding **best practices** in formatting, commenting, and functional logic.

#### First Step
The process calls for me to utilize and examine the `Milestone1.py` file. The file contains the preamble for utilizing the `RPi.GPIO` package with setup, setup mode BCM, and warnings declared as false.

The first substantial part of the application is where we configure PWM to 18 at 60Hz (Refer to [[Section 2.7 Pulse width modulation]]).

```python
pwm18 = GPIO.PWM(18, 60)
```

There's a confliction with the next code assignment vs documentation. The PMW Lab guide details a duty cycle of 50% being started on pwm18 but the code itself reflects a duty cycle of 0%.

```python
pwm18.start(0)
#pwn18.start(50) # detailed in lab guide.
```

This script appears to utilize the original configuration defined in module one for our breakout board. which can be observed below.

![[Turned On.jpg]]

#### Step One and a half
This isn't apart of the official project guide, but I feel its a worthwhile step to employ and document. I realized that in this project document they want us to make changes directly on the Ubuntu Server OS with a terminal editor like nano or vim. I'd prefer to keep using my IDE, PyCharm, on my local device. The problem with that is getting a working development environment that can rapidly deploy tests on the remote Raspberry Pi with the breakout board.

1) Navigate to the Pi charm settings by clicking the four horizontal bars and making it to the "Settings" or use "ctrl + alt + s". 
   ![[settings.png|250]]
2) Now Select your project drop down from the left hand list. Click "Python Interpreter". Select "Add Interpreter" on the right of the window followed by "On SSH" (Disregard the improper highlighting of "Add Local Interpreter").
   ![[Interpreter.png]]
3) Fill in the host, port, username. Follow the guided prompt to finish adding the SSH connection and navigate to your python interpreter located on local device. On Ubuntu Server it's typically located at `/usr/bin/python3`.
4) Now you're set up to execute code remotely!

#### Step Two
Now I am to understand the changes in the frequency. I understand that the lab guide now details using the start to set to fifty so that we can observe effects of a changing PWM frequency. I set the start duty cycle to fifty as described `pwm18.start(50)`. The frequency is define at `pwm18 = GPIO.PWM(18, 60)` where sixty is the frequency in Hz. Anything <= 60 is likely to result in a continuous lighting effect.

- There's nothing noticeable about a PWM frequency above 60 combined with a duty cycle of 50.

- Changing the PWM frequency to 30 with a duty cycle of 50 creates a noticeable fast blink.

- At a frequency of 1 with a duty cycle of 50 creates a very slow blink.

```
Frequency = The rate in which the ON/OFF state is switched.

Duty Cycle = The percentage of time in which the light is lit for that frequency cycle. 
```

Imagine a frequency cycle that lasts a total of one second. Imagine a duty cycle of 50%. Half of that second would be in an on state and the other half in an off state. So what's the point? Why not just keep the duty cycle at 100%? Well lowering the duty cycle incrementally or keeping it at different rates allows developers to create effects such as blinking or fading. Additionally a lower duty cycle in addition to a frequency above 60 creates a dimmed brightness for the LED.

#### Step 3
Now it's time to understand the duty cycle. I know that from the previous experiments that the larger the percentage the longer the light stays on. Lower the percentage the longer the light stays off. Here are a few findings:

- **100% Duty Cycle and 60 Hz** yielded a bright continuous light.
- **50% Duty Cycle and 60 Hz** yielded a slightly dimmer, but still bright light.
- **25% Duty Cycle and 60 Hz** yielded a even dimmer light.
- **5% Duty Cycle and 60 Hz** yielded a very dim light.

As the duty cycle reduces the brightness goes down. Its actually the LED flipping between ON and OFF states and only being on for a fraction of that full 60 Hz cycle that it doesn't power completely up before being in an OFF state again. 

#### Step 4
Now I am to fade the LED in and out. The guide details to set the starting duty cycle to zero. Additionally, create a for loop to update the duty cycle from 0-100 at increments of five with a sleep of 0.1s. This would look like as described in the guide:
```python
# Loop from 0 to 100 in increments of 5  
for duty_cycle in range(0, 100, 5):  
    # update the dutyCycle accordingly  
    pwm18.ChangeDutyCycle(duty_cycle)  
    
    # pausing 1/10th of a second between each update
     time.sleep(0.1)
```

I should note that their implementation does have a bug. This code as provided would only get to a duty cycle of 95% because `range(x, y, z)` creates an array that starts at `x` and end exclusively at `y` not inclusively. So it would be better to do `range(0, 101, 5)` otherwise a full duty cycle 0-100 isn't achieved.

This code snippet yields a lighting effect that starts at an OFF state and increases brightness until it reaches maximum lighting.

Now the inverse:
```Python
# Loop from 100 to decrements of -5 reaching zero  
for duty_cycle in range(100, -1, -5):  
    # update the dutyCycle accordingly  
    pwm18.ChangeDutyCycle(duty_cycle)  
    # pausing 1/10th of a second between each update  
    time.sleep(0.1)
```

Now that both loops are implemented the LED does a smooth transition from OFF to ON state in a slow and smooth pulse. Again I set the range to be inclusive by setting the end of the range to -1.
#### Step 5
Step five details the need to implement a clean up for the GPIO when a keyboard interrupt is introduced. This step is redundant because the provided template came with a Try/Catch clean up for a keyboard interrupt already. This looks like:
```python
# Preamble to GPIO program such as variable assignments and config.
repeat = true
while repeat:
	try:
		#Do GPIO actions here
		pass
	except KeyboardInterrupt:
		# Stop the PWM instance on GPIO line 18  
		print('Stopping PWM and Cleaning Up')  
		pwm18.stop()  
		GPIO.cleanup()  
		repeat = False
```
#### Step 6
Recording of the pulsing effect:
![[Module_One_Proof.mp4]]

#### Lab Questions
1) **At what frequency can you see the LED start to blink?**
   I was able to see the LED start to blink sub-60Hz but I found it was most perceivable at a fast rate at 30 Hz.
   
2) **At what duty cycle is the intensity of the LED perceptibly diminished from the initial 50%**
   I noticed the light was perceptibly diminished at a duty cycle of sub-25% duty cycle. I greatly noticed the light diminished below 10%.
   
3) **When changing the duty cycle of the PWM, the loop used an increment of 5 every tenth of a second. Was this perceptibly smooth? If not, what could you change to improve the visual response? Why?**
   I did notice that at increments of 5 it stuttered slightly between transitions and didn't feel as smooth as it could. I would recommend adjusting the duty cycle increments so they adjust at rates of 1 instead. This would provide the maximum performance in terms of seamless transitions.
   
4) **What function sets PWM frequency for GPIO line?**
   This is `pwm18 = GPIO.PWM(18, 60)` where sixty is the frequency in Hz.
   
5) **What function sets the duty cycle for a GPIO line?**
   This is accomplished initially by `pwm18.start(0)` where zero is the duty cycle. In the described assignment loops the duty cycle is adjusted for the GPIO line with `pwm18.ChangeDutyCycle(duty_cycle)` where `duty_cycle` is the float percentage of the duty cycle.