---
tags:
  - latency
  - embedded
---
### Questions to still figure out
- What is a synchSM

***
### Notes
An engineer can **reduce the synchSM period** and the **state sequence** between detecting the input event and generating the output event to reduce the overall latency in a system. These are **competing** design goals though. When dealing with a competing design consideration the engineer needs to identify which tradeoffs work best for their project. In this case we're considering **minimizing latency** and **minimizing microcontroller utilization**.

***

Example 2.2.1: Doorbell system.

![Doorbell.](https://zytools.zybooks.com/zyAuthor/ProgEmbSys/26/IMAGES/dbd9141f-878e-886a-2c69-25ea5ac8f4e1 "doorbell")  

Consider an electronic doorbell, with a button connected to A0, and B0 connecting to a bell. Given are the following timing specifications. The minimum button press length to be considered is 400 ms. The minimum separation between presses (from release to next press) is 500 ms. The maximum latency between a press and the start of the bell ringing should be 100 ms. When a valid button press is detected, the bell should ring for 1 second and then stop ringing until the next distinct button press. The following table lists how each timing specification constrains the synchSM:

|Timing specification|Constraint|
|---|---|
|Minimum press length 400 ms|Period should be < 400 ms|
|Minimum separation time between a button release and a button press: 500 ms|Period should be < 500 ms|
|Maximum latency between press and bell: 100ms|synchSM period should be <= 100 ms, and state sequence should ensure latency <= 100 ms|
|Bell rings for 1 sec|Period should evenly divide 1000 ms|
|Minimize processor utilization|Period should be as large as possible|

  

Based on the constraints, the largest possible period is 100 ms. Other possible periods are 50, 25, 20, 10, ... (divisors of 100), but a larger period is preferred to minimize microcontroller utilization. We can create the following synchSM:

![Doorbell system state machine. The period is 100 ms. The variable is unsigned char cnt. The 2 states are WaitPress and Ring. The starting state, WaitPress, has action B0 = 0;, a transition to itself with condition !A0, and a transition to Ring with condition A0 / cnt = 0;. Ring has action B0 = 1; cnt++;, a transition to itself with condition cnt &lt; 10, and a transition to WaitPress with condition !(cnt &lt; 10).](https://zytools.zybooks.com/zyAuthor/ProgEmbSys/26/IMAGES/06a9ae8c-60e3-7a36-657e-46ccd522786f)  

The designer may evaluate the synchSM and note that the bell ring will occur 100 ms or less after A0 becomes 1, as also validated by the timing diagram obtained using RIBS/RIMS/RITS.

***

### Provided Links for further exploring
- [Wikipedia: Latency(Engineering)](http://en.wikipedia.org/wiki/Latency_%28engineering%29)