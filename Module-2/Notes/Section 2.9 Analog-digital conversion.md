---
tags:
  - embedded
  - analog
  - digital
  - input
  - output
  - sensor
---

An **analog-to-digital** or **ADC** or **A2D** is a device that converts a varied voltage signal or **analog signal**, typically an output from a sensor, and converts it to a **digital signal** of bits that a microcontroller can utilize. Devices like an ADC are considered a **mixed-signal** device because they handle both analog and digital Input/Output.

**Analog-to-Digital Conversion Example**
![An analog input, where the signal can take on any value, enters the ADC. The digital output contains signals that are integers, such as 1, 2, 3.](https://zytools.zybooks.com/zyAuthor/ProgEmbSys/26/IMAGES/embedded_image_1_ee71c16c-3865-dfe8-7245-5346e3d38da8_lYqbN4jVKJadxnFCf7Fe.png)

An analog-to-digital conversion process requires establishing three basic parameters:

- The first parameter is the range of analog values to be converted, meaning the highest and lowest possible voltages. For example, an ADC may convert an analog voltage in the range of **-2.0 volts to +2.0 volts**.
- The second parameter is the range of digital values to correspond with the analog voltages. For example, the ADC may convert to digital values in the range of **-128 to +127**. The conventional way of describing the digital range of an ADC is in number of bits used to represent an analog value. **The number of bits used by an ADC is also referred to as the ADC’s precision**. The above digital values would be for an **8-bit conversion**.
- The third parameter is the rate at which an ADC is capable of converting analog values to digital. For example, the ADC may be capable of converting 1000 samples per second. By convention, this rate is referred to as the **sampling rate**.

It should be considered that there is a degree of error when converting analog to digital. This is called the **quantization error**. In the example described about we can see that the total volt range is 4 volts (-2v to +2v). We can also see the digital value range is (-128 to +127) which is a total of 256 bits. We can find the quantization error rate by performing this calculation: `4/256=0.015625`. This value is the quantization error, in other words its the voltage range needed to change before the digital conversion registers a change.

Most systems designers nowadays do not build their own ADC because how readily available they are. These ADC's come in two forms:
- **Parallel interfaces** are simpler to use but require more system resources.
- **Serial interfaces** require very little resources at the expense of simplicity as they require a complicated handshake and communication standard.
