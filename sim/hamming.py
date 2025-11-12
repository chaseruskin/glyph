'''
Python behavioral model for standard hamming code error-correction code.

Single error correction, double error detection (SECDED) using "extended
hamming code" due to additional parity bit in 0th position to check overall 
block parity.

In this script, an EVEN parity represents an even number of 1's, therefore
the parity bit is set to 0. An ODD parity represents an odd number of 1's,
therefore the parity bit must be set to 1 to achieve even parity.

The implementation is generic over the i number of PARITY_BITS, where i > 1.
The Hamming-code is unreliable with errors > 2 (errors may cancel or be 
unrecoverable).

To execute unit tests for this module, run: `python -m unittest hamming.py`.

References:
- "How to send a self-correcting message (Hamming codes)" - 3Blue1Brown
 https://www.youtube.com/watch?v=X8jsijhllIA
 
- "Hamming code" - Wikipedia
 https://en.wikipedia.org/wiki/Hamming_code#[7,4]_Hamming_code
'''

import unittest
from math import log
from typing import List
from typing import Tuple
import random
import math
from . import glyph as gl

# the number of parity bits (excluding additional parity bit for SECDED)
# all other constants are derived from defining the number of parity bits
PARITY_BITS = WIDTH = 5

TOTAL_BITS = 2**PARITY_BITS

DATA_BITS = 2**PARITY_BITS-PARITY_BITS-1

RATE = DATA_BITS/TOTAL_BITS

class HammingCodec:

    def __init__(self, k: int):
        '''
        Construct a new Hamming Codec instance.
        '''
        self.data_bits = k
        self.parity_bits = HammingCodec.get_parity_bits(k)

    @staticmethod
    def get_parity_bits(k: int):
        '''
        Finds _P_, the number of required parity bits (excluding zero-th), such
        that K + 1 = 2^P - P.
        '''
        d = k + 1
        # find P such that D = 2^P - P
        p = 2
        while True:
            if d <= 2**p - p:
                break
            p += 1
        return p

    def get_total_bits_len(self) -> int:
        return self.data_bits+self.get_parity_bits_len()+1

    def get_parity_bits_len(self) -> int:
        return self.parity_bits

    def get_data_bits_len(self) -> int:
        return self.data_bits

    def _create_hamming_block(self, chunk: List[int]) -> List[int]:
        '''
        Inserts parity bits at the corresponding power-of-2 indices.

        Frames the data with the parity bits.
        '''
        # position 0 along with other powers of 2 are reserved for parity data
        chunk.insert(0, 0)
        for i in range(0, self.get_parity_bits_len()):
            chunk.insert(2**i, 0)
        return chunk

    def _encode_hamming_ecc(self, block: List[int]) -> List[int]:
        '''
        Sets the parity bits for the Hamming-code block.

        Includes setting the overall parity of the block at 0th bit.
        '''
        # questions to capture redundancy for each parity bit
        parities = []
        for i in range(0, self.get_parity_bits_len()):
            coverage = self._get_parity_coverage(i)
            # print('p:', i, coverage)
            data_bits = [block[j] for j in coverage]
            # data_bits = [block[j] for j in coverage]
            # print('group', i, data_bits)
            block[2**i] = gl.get_parity(data_bits)
            parities += [block[2**i]]
            pass
        # print('parities', parities)
        # set overall parity for SECDED
        block[0] = gl.get_parity(block)
        return block


    def _get_parity_coverage(self, i: int) -> List[int]:
        '''
        Returns the list of indices covered by the i-th parity bit.
        '''
        space = (self.get_total_bits_len())
        # print(space)
        subset = []
        # check the i-th bit positions
        for s in space:
            if s[self.get_parity_bits_len()-i-1] == '1':
                subset += [s]
        # convert from binary to decimal for target indices
        return [int('0b'+x, base=2) for x in subset]


    def encode(self, message: List[int]) -> List[int]:
        '''
        Transforms and formats a plain `message` into an encoded hamming-code
        block.
        '''
        block = self._create_hamming_block(message)
        return self._encode_hamming_ecc(block)


    def _destroy_hamming_block(self, chunk: List[int]) -> List[int]:
        '''
        Pops parity bits at the corresponding power-of-2 indices, revealing
        the data.

        Deframes the parity bits from the data.
        '''
        # remove parity bits
        for i in range(self.get_parity_bits_len()-1, -1, -1):
            chunk.pop(2**i)
        chunk.pop(0)
        return chunk


    def decode(self, block: List[int]) -> Tuple[List[int], int, int]:
        '''
        Transforms and formats an encoded hamming-code `block` into a decoded 
        message.

        Returns `(message, sec, ded)`.
        '''
        (block, sec, ded) = self._decode_hamming_ecc(block)
        return (self._destroy_hamming_block(block), sec, ded)


    def _decode_hamming_ecc(self, block: List[int]) -> Tuple[List[int], int, int]:
        '''
        Decodes the hamming-code. 
        
        Corrects single-bit errors and detects double-bit errors. 
        
        Returns the fixed block and the valid signal.
        '''
        # answer the question for each parity bit
        answer = ''
        # block parity
        par_block = gl.get_parity(block)
        # questions to capture redundancy for each parity bit
        for i in range(self.get_parity_bits_len()-1, -1, -1):
            coverage = self._get_parity_coverage(i)
            data_bits = [block[j] for j in coverage]
            parity = gl.get_parity(data_bits)
            if parity == 0:
                # rule out the space
                answer += '0'
            else:
                # include this space
                answer += '1'
            pass

        # determine if there are unrecoverable errors or zero errors
        if par_block == 0:
            # check if two errors were detected
            if answer.count('1') > 0:
                # print("info: Detected a double-bit error (unrecoverable)")
                return (block, 0, 1)
            # check if there were zero errors
            else:
                # print("info: 0 errors detected")
                return (block, 0, 0)

        # otherwise, use the parity bits to pinpoint location of error to correct
        i = int('0b'+answer, base=2)
        # print("info: Error index:", i, "("+answer+")")

        # fix block at the pinpointed error index according to parity bits
        try:
            block[i] ^= 1
        except:
            # if list index is out of range, then it was errors > 2
            pass
        return (block, 1, 0)
    pass


def total_bits(parities: int) -> int:
    '''
    Computes the number of total bits in the encoded hamming block.
    '''
    return 2**parities


def data_bits(parities: int) -> int:
    '''
    Computes tehe number of information bits in the encoded hamming block.
    
    Assumes the 0th bit is used for an additional parity bit.
    '''
    return 2**parities-parities-1


def display(block: List[int], width=None, end='\n'):
    '''
    Formats the Hamming-code block in a square arrangement.
    
    Use `width` to set a custom number of bits to print per line.
    '''
    # auto-detect width for pretty-formatting block
    width = int(log(len(block), 2)) if width == None else width
    i = 0
    while i < len(block):
        if i > 0 and i % width == 0:
            print()
        print(block[i], end=' ')
        i += 1
    print(end=end)
    pass


def partition(msg: List[int]) -> List[List[int]]:
    '''
    Splits a long string of bits `msg` into a list of chunks with `DATA_BITS`
    size to be formed into Hamming-code blocks.
    '''
    chunks = []
    ctr = 0
    while ctr < len(msg):
        chunk = [0] * DATA_BITS    
        for i in range(0, DATA_BITS):
            chunk[i] = msg[ctr]
            ctr += 1
            # exit early if not enough bits in the message to fill the current chunk
            if ctr == len(msg):
                break
        chunks += [chunk]
        pass
    return chunks


# --- Logic --------------------------------------------------------------------

# even parity = even number of 1's -> set bit to 0
# odd parity  = odd  number of 1's -> set bit to 1 to achieve to even parity

if __name__ == '__main__':
    if PARITY_BITS < 2:
        exit("error: PARITY_BITS must be greater than 1")

    # 33 bits
    message = [
        0, 0, 1, 1, 0, 0, 0, 1,
        1, 1, 0,
        0, 1, 1, 0, 0, 1, 1, 0, 
        1, 0, 0, 0, 0, 1, 0, 0, 
        0, 0, 1, 1, 1, 0, 1, 1, 
        0, 1, 0, 1, 1, 1, 0, 0,
        1,
    ] 

    # generate random message bits
    message = [random.randint(0, 1) for _ in range(0, DATA_BITS)]

    ham = HammingCodec(PARITY_BITS)

    # divide message into 11-bit chunks
    chunk = partition(message)
    tx_message = chunk[0]
    print("Sender's Data:", tx_message)

    # reserve locations for parity bits
    block = ham._create_hamming_block(tx_message.copy())
    print("Formatted hamming-code block:")
    display(block)

    # encode using hamming-code
    encode = ham._encode_hamming_ecc(block)
    print("Transmitting:")
    display(encode)

    # simluate transmitting bits over a noisy channel
    packet = gl.transmit(encode.copy(), spots=[], noise=None)
    print("Received:")
    display(packet)

    # decode using hamming-code
    (decode, valid) = ham.decode_hamming_ecc(packet)

    # continue to deframe if the message was recoverable
    if valid == 1:
        print("Corrected:")
        display(decode)
        assert(encode == decode)

        # remove parity bits
        rx_message = ham._destroy_hamming_block(decode)
        print("Receiver's Data:", rx_message)
        assert(rx_message == tx_message)

    # if 2 errors detected, tell sender to resend the message
    else:
        print("info: Receiver's data is corrupted (unrecoverable errors)")
    pass


class TestHamming(unittest.TestCase):
    '''
    Test cases for the Hamming Codec.
    '''

    pass
