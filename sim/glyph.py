import random
import math
import unittest

def pack(num: int) -> list:
    '''
    Converts an integer into its 1s and 0s (MSB to LSB) as a list.
    '''
    return [int(bit) for bit in bin(num)[2:]]


def unpack(iter: list) -> int:
    '''
    Converts a list of 1s and 0s (MSB to LSB) into an integer.
    '''
    num = 0
    for (i, b) in enumerate(iter[::-1]):
        num = (b << i) | num
    return num


def get_parity(arr: list, even=True) -> bool:
    '''
    Checks if the `arr` has an odd amount of 0's in which case the parity bit
    must be set to '1' to achieve an even parity.

    If `make_even` is set to `False`, then odd parity will be computed and will
    seek to achieve an odd amount of '1's (including parity bit).
    '''
    # count the number of 1's in the list
    return (arr.count(1) % 2) ^ (even == False)


def get_bin_space(n: int) -> list:
    '''
    Returns binary strings for the possible combinations of input from
    0 to `n`.
    '''
    space = []
    for m in range(0, n):
        space += [bin(m)[2:].zfill(math.ceil(math.log2(n)))]
    return space


def transmit(block: list, noise: int=0, spots: list=None) -> list:
    '''
    Transmits a code block over a noisy channel that may flip 0, 1, or 2 bits.

    Use `spots` to explicitly declare which positions to flip.
    Use `noise` to explicitly set the number of flips in the transmission.
    '''
    # use custom-defined indices to flip
    if spots is not None and len(spots) > 0:
        for s in spots:
            block[s] ^= 1
        return block
    if spots is None:
        spots = []
    # use random-defined amount of spots and locations
    for _ in range(0, noise):
        # select a random index not already flipped
        flip = random.randint(0, len(block)-1)
        while spots.count(flip) > 0:
            flip = random.randint(0, len(block)-1)
        # reverse the bit
        block[flip] ^= 1
        # remember that position is now flipped
        spots += [flip]
    # print("\nBits flipped during transmission:", spots, end='\n\n')
    return block


class TestGlyph(unittest.TestCase):
    '''
    Test cases for the general glyph code.
    '''

    def test_get_bin_space(self):
        space = get_bin_space(2**1)
        self.assertEqual(space, ['0', '1'])

        space = get_bin_space(2**2)
        self.assertEqual(space, ['00', '01', '10', '11'])

        space = get_bin_space(2**3)
        self.assertEqual(space, [
            '000', '001', '010', '011',
            '100', '101', '110', '111'
        ])

    def test_transmit(self):
        # flip 1 location
        message = [0, 1, 1]
        transmit(message, spots=[0])
        self.assertEqual(message, [1, 1, 1])
        # flip 2 locations
        message = [0, 1, 1]
        transmit(message, spots=[0, 2])
        self.assertEqual(message, [1, 1, 0])
        # flip 1 bit
        message = [0, 1, 1, 0]
        transmit(message, noise=1)
        self.assertNotEqual(message, [0, 1, 1, 0])
        # flip 0 bits
        message = [0, 1, 1, 0]
        transmit(message, noise=0, spots=[])
        self.assertEqual(message, [0, 1, 1, 0])

    def test_get_parity(self):
        # even parity
        check = get_parity([1, 0, 0])
        self.assertEqual(check, 1)

        check = get_parity([1, 0, 0, 1])
        self.assertEqual(check, 0)

        # odd parity
        check = get_parity([1, 0, 0, 1], even=False)
        self.assertEqual(check, 1)

        check = get_parity([1, 0, 1, 1], even=False)
        self.assertEqual(check, 0)
