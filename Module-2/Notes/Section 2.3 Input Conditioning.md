---
tags:
  - embedded
  - input_conditioning
  - sensor
  - filtering
---
#### Notes
 Sensors are rarely accurate and as such a microcontroller will have to account for these imperfections with fine tuning. This fine tuning is known as **input conditioning**. 

##### Figure 2.3.1: Button bouncing.

![Timing diagram of button bouncing. A0 changes from 0 to 1 at 0.3 seconds, 1 to 0 at .4 seconds, 0 to 1 at 0.5 seconds, and 1 to 0 at 1 second. A sampling at 0.3 seconds senses 1, a sampling at 0.4 seconds senses 0, and a sampling at 0.5 seconds senses 1.](https://zytools.zybooks.com/zyAuthor/ProgEmbSys/26/IMAGES/embedded_image_1_8969ee8d-5523-ae1d-44f8-fd4753ccc722_bDnKtBRH5if6dBP4VK7n.png)
Consider the figure above and the scenario of a button like input that has a ball dropped on it. The ball may bounce when it hits the input sensor. We wouldn't want to count the ball being dropped twice so the design consideration needs to account for the lapse of input at the 0.5s mark. Buttons in general as they degrade or come from poor quality may have this bouncing input signal even when the input signal appears constant in person.

This isn't the only scenario in which an input signal will capture multiple events when you only desire to capture the entirety of it. To ensure that we're handling this input we employ a tactic known as **button debouncing**. This task is a design consideration that eliminates the bouncing input signal. In **modern buttons** we can see input bouncing doesn't occur for more than 10-20ms at a time so most design patterns account for a **50ms Sampling Period** in their button debouncing design.

**Filtering** is the more general term for plainly ignoring certain input events. In a general sense its common to ensure that a input signal is captured for two consecutive sampling periods. Filtering is a mitigation technique so consider the likelihood of a glitch to occur in your system. This won't completely eliminate the possibility of a glitch but should significantly reduce it if possible.

Filtering can be done in an inverse state as well. This means that we might consider two sample periods of a zero state before accepting that the state has changed to an off state.

The solution of reducing this signal bouncing **may not even be a software solution**. Some projects may invest in **better quality sensor** that have cleaner output (less bounce), **insulating sensors and wires** to prevent electromagnetic interference, or **introduce a capacitor** to even the input.

**Electromagnetic interference** can cause random state changes, typically for short bursts of time, on sensors and wires.






