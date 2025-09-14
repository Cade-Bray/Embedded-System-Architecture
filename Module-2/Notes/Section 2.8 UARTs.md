---
tags:
  - embedded
  - serial
  - UART
  - RIMS
---

### Notes

A UART is a local hardware pin that transmits a byte one bit at a time over a single pin. This is typically written over a line called **rx** and read over a line called **tx**. The `RIMS.h` we use has a function that can enable this communication called `UARTOn()`. There is usually a flag raised during transmission called `TxReady`. This global is set to zero when transmitting and one when it can be written too. Writing to `T` while it isn't ready will result in corruption. 

**Example** - Basic outputting data using UART
```C
void main() {
	UARTOn(); // Activate the UART
	while(1) {
		while(!TxReady); // Holding pattern for TxReady
		T = 0x61; // Transmit data serially over UART output pin
	}
}
```

**Example** - Basic receiving input data using UART
```C
volatile unsigned char RxFlag = 0;
void RxISR() { // This function is called automatically when UART gets data
	RxFlag = 1;
}

void main() {
	UARTOn();
	while(1) {
		while(!RxFlag); // Wait until UART revieves data
		RxFlag = 0; // We're reading the data
		B = R; // Write recieved data to B output
	}
}
```

Until R is read by the program, UART will not overwrite the value of R. A common error that programmers make is to forget to turn on UART. Another common issue is to neglect reading R even when you don't need it. R won't get overwritten until you do. `RxISR()` is automatically called when a full byte of data is transmitted. 