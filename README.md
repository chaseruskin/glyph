# Glyph

Hardware descriptions of error correction codes (ECC).

## Codes

The currently implemented ECCs include:
- [Hamming Code](#hamming-code)

### Hamming Code

The implementation uses the "extended" Hamming code, where the 0th bit is an additional parity check against the entire data block for double-error detection (DED). The encoder and decoder are both implemented in purely combinational logic. The encoder and decoder are both parameterizable by the number of data bits, `K`.

A single erroneous bit can be corrected for each Hamming code block (SEC). Any block received with an even number of errors `e` with `e` > 0 will not be valid. A block received with an odd number of errors `e` with `e` > 1 may self-correct to the incorrect original message.

The following table highlights some example data sizes, along with their Hamming code block size and rate:

Data Bits (`K`) | Parity Bits | Block Size | Rate  
--- | ---    | --- | --- 
1 | 3       | 4   | 1/4 = 0.250
4 | 4       | 8   | 4/8 = 0.500
11 | 5       | 16  | 11/16 ≈ 0.688
26 | 6       | 32  | 26/32 ≈ 0.813
32 | 7       | 39  | 32/39 ≈ 0.821
57 | 7       | 64  | 57/64 ≈ 0.891
64 | 8       | 72  | 64/72 ≈ 0.889
120 | 8       | 128 | 120/128 ≈ 0.938
247 | 9       | 256 | 247/256 ≈ 0.965

## References

- "How to send a self-correcting message (Hamming codes)" - 3Blue1Brown  
https://www.youtube.com/watch?v=X8jsijhllIA

- "Hamming code" - Wikipedia  
https://en.wikipedia.org/wiki/Hamming_code#[7,4]_Hamming_code

- "Parity bit" - Wikipedia  
https://en.wikipedia.org/wiki/Parity_bit