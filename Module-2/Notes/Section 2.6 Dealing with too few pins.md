---
tags:
  - embedded
  - GPIO
  - input
  - output
  - pins
---

### Notes

##### Time-multiplexed output with registers
Assume that you want to output a signal to turn on or off an LED. Assume your microcontroller has 8 output pins. What happens when we want to output to 10 LEDs? The solution is adding external registers. How these registers work is with pulsing the data in sets. Assume that a register knows that any output that contains a 1 bit is intended for it. So If a microcontroller outputs `10001111` where the first bit in the upper nibble indicates what register and the lower nibble reports which LEDs to turn on. This was be saying, "Register turn on all four LEDs you control". This would allow the microcontroller to handle four additional outputs.

##### Time-multiplexed output with rapid refresh
Let's assume you don't have external registers. You can still achieve this task with transistors. A transistors amplifies a voltage and for that reason will hold a charge for a duration of time. You can rapidly switch your outputs to different LEDs. As long as the refresh rate for the transistors is fast enough there shouldn't be any noticeable difference in the LEDs 'on' state. Humans won't notice a difference at roughly 50-100 times per second. 

##### Time-multiplexed input
Now consider receiving input from multiple sources beyond how many inputs you may have. Consider a keypad, each row is connected to the microcontroller as four input pins. The output of those pins correspond to the four columns that the keypad has which creates a full circuit that constantly reports one. The buttons on the keypad are external pull-ups which pull the voltage down when triggered thus reporting a change of state to zero.

Now that the system is configured in such a way that a microcontroller can see which row/column reports zero/one we can determine which buttons are pressed. We then scan each button at a fast rate detecting a button press. This scanning rate needs to be fast enough that it won't miss a scanned button state change.