---
tags:
  - embedded
  - Signal
  - Wave
  - Cycle
---

### Notes

##### Signal, Cycle, and Wave
Some embedded systems generate periodic sequences of output pulses. 
![[periodic signal.png]]
Now consider this time graph. The first pulse duration is 600ms. The second pulse that occurs at 1.4s is 600ms. Since this is a reoccurring pattern of the first 400ms being low and the last 600ms are high we know that this is a **periodic signal** because of the repeating pattern. We can now determine the **duty cycle**, which is the percentage of high periods, by calculating `600ms / 1000ms = 60%`. Any duty cycle that is exactly 50% would be referred to as a **square wave**. You can program a **pulse width modulator** or **PWM** to keep a specific duty cycle. 

One use of a PWM is to keep the exact pace of a **DC Motor**. Products like a cordless drive might use a PWM. 

##### Additional Readings
- Wikipedia: pulse width modulation - http://en.wikipedia.org/wiki/Pulse-width_modulation
- Wikipedia: DC Motor - http://en.wikipedia.org/wiki/DC_motor