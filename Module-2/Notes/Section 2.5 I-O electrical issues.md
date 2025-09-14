---
tags:
  - embedded
  - resistor
  - buffer_ic
---

### Notes

##### Changing voltage
Some devices you connect to a microcontroller may have various needs as far as voltage. If the device needs a higher voltage we add what's called a **Buffer IC** which will increase the voltage to the desired amount. Inversely we can add a **Load Resistor** to the circuit which will lower the voltage to the desired amount. This would be useful when working with LEDs.

##### Pull-up Configuration
![A system with an input 0 through a disconnected button is read as 1 by the micro-controller. A system with an input 0 through a connected button is read as 0 by the microcontroller.](https://zytools.zybooks.com/zyAuthor/ProgEmbSys/26/IMAGES/embedded_image_1_26234ff4-3288-8394-5346-c297ed6d4dcf_bDnKtBRH5if6dBP4VK7n.png)
What is known as a pull-up configuration allows a system to report a value of one when the circuit is disconnected and report the actual intended value, in the figure is described as zero, when the circuit is complete. Pull-up configurations are useful in what's known as a passive button. 

![[Pull-up config example.png]]

The example above is what happens when you pass the ground through an external pull-up configuration. When the pull-up is in the 'on' state we can observe a completed circuit which pulls the power level down resulting in a '0' value reported. When the pull-up is 'off' we can observe the voltage rise to a point that the microcontroller can detect an input resulting in a '1' state.

