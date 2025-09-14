---
tags:
  - embedded
  - glitches
  - filtering
---
### Notes

Code that will result in glitches on B as 1s are found and B is incremented
```C
#include "RIMS.h"

unsigned char GetBit(unsigned char x, int k) {
	// x & 00000001 << k where k will move the one to the desired location
	// The & operator is a bitwise operator. Makes it so the two values return one 
	// if they're both one.
	return ((x & (0x01 << k)) != 0); // Returns True (1) if that bit location is 1
}

void main() {
	unsigned char i;
	B = 0; // initialized output
	while(1) { // constant loop
		B = 0; // set to zero
		for (i=0; i<B; i++) { // for each bit in B, B is a 8bit char
			if(GetBit(A, i)){ // If 
				B++; // Incriment B. This is constantly being updated.
			}
		}
	}
}
```

This is code that won't result in glitches
```C
#include "RIMS.h"

// Nothing changed with this function
unsigned char GetBit(unsigned char x, int k) {
	// x & 00000001 << k where k will move the one to the desired location
	// The & operator is a bitwise operator. Makes it so the two values return one 
	// if they're both one.
	return ((x & (0x01 << k)) != 0); // Returns True (1) if that bit location is 1
}

void main() {
	unsigned char cnt; // Using a temp value as an intermediary to avoid glitches
	unsigned char i;
	while(1) {
		B = 0;
		for (i=0; i<B; i++) {
			if (GetBit(A, i)) {
				cnt++;
			}
		}
		B = cnt; // Assignment outside of the Bit checking section
	}
}
```

This program is checking each bit in A and assigns the count to B. In the second version B isn't updated until all bits are checked which helps avoid glitching. This was provided by the textbook and I'd recommend even pulling the `B = 0` outside of the while loop so you don't get an immediate reassignment back to zero. This would cause bouncing on the input as well. That wasn't included in the textbook though.