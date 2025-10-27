# Embedded System Architecture
This project utilizes a raspberry pi or other single board computer, python-statemachine dependencies, and 
a breakout board with a GPIO connector ribbon. This project creates a mock thermostat that utilizes a temperature and
humidity sensor over I2C connections. The thermostat has a 16x2 display that outputs information for the user.

I feel as though I did well on the state machine implementation and documentation of code. I believe that strong
documentation is a requirement for any project that has the hope of continued iterations beyond its initial deployment.
I feel as though I could improve on the embedded device wiring organization. Many wires overlap and produce less than
ideal user experiences. Despite it being a prototype, effort should be made to see if such a thermostat is viable both 
functionally, securely, and with satisfactory user experience.

During this project I've added many tools to my arsenal for future developments. Most of these advancements were made in 
the realm of development tools. I was able to successfully configure a remote development environment onto a mock embedded 
device. This was accomplished with the PyCharm SSH and SFTP functionality. These tools, once configured, allowed for rapid
prototyping of embedded devices and ease of debugging.

Working with state machines will continue to be a useful tool in future embedded projects as they're the go-to architecture
for such a platform. While the project template was provided to us, I still felt as though the readability could've been
further enhanced. I spent time rebuilding the documentation of the project to be in line with python PEP recommendations.
These recommendations are industry standard and are proven to promote readability and maintainability.

Moving forward I'd like to explore working with microcontrollers as the implementation device instead of a single board 
computer as I believe it could yield better outcomes in system performance as the overhead is reduced.

https://youtu.be/PNeJJ2FwW3w
