import glyph as gl
import random
import unittest

class GolayCodec:
    '''
    Class to implement the extended Golay code.

    Much code adapted from Hank Wallace (http://aqdi.com/articles/using-the-golay-error-detection-and-correction-code-3/).
    '''

    POLY = 0xAE3

    def __init__(self):
        '''
        Construct a new Golay Codec instance.
        '''
        self.block_len = 24
        self.message_len = 12

    def encode(self, data: int) -> tuple:
        '''
        Transforms and formats a plain `message` into an extended Golay block.

        Returns `(check, parity)`.
        '''
        # print(bin(data))
        rev_data = int('{:012b}'.format(data)[::-1], 2)
        # print('data: ', bin(rev_data)[2:].zfill(12))
        cw = rev_data & 0xfff
        for _ in range(0, 12):
            if cw & 0b1:
                cw ^= self.POLY
            cw = cw >> 1
        # print(bin(cw))
        rev_cb = int('{:011b}'.format(cw)[::-1], 2)
        # print(hex(rev_cb))
        parity = gl.get_parity(gl.pack(rev_cb << 12 | rev_data))
        # print('check:', bin(rev_cb)[2:].zfill(11))
        # print(bin(self.assemble_cw(data, rev_cb)))
        return (rev_cb, parity)

    def syndrome(self, cw: int) -> int:
        '''
        Calculates and returns the syndrome of a [23,12] Golay codeword `cw`.
        '''
        for _ in range(0, 12):
            if cw & 0b1:
                cw ^= self.POLY
            cw = cw >> 1
        syn = cw << 12
        return syn
    
    def decode(self, data: int, check: int, parity: int) -> tuple:
        '''
        Transforms and formats an encoded hamming-code `block` into a decoded 
        message.

        Returns `(message, tec, qed)`.
        '''
        tec = 0
        qed = 0
        # combine into single codeword
        cw = self.assemble_cw(data, check)
        # print(bin(cw))
        # save off the original codeword
        og_cw = cw
        # number of errors encountered
        errs = 0
        # initial syndrome weight threshold
        w = 3
        # -1 = no trial bit flipping on first pass
        j = -1
        mask = 1
        # flip each trial bit
        while j < 23:
            # toggle a trial bit
            if j != -1:
                # restore last trial bit
                if j > 0:
                    cw = og_cw ^ mask
                    # point to next bit
                    mask += mask
                # flip the next trial bit
                cw = og_cw ^ mask
                # lower the threshold while bit diddling
                w = 2
            # look for errors
            s = self.syndrome(cw)
            # an error exists!
            if s > 0:
                # check syndrome of each cyclic shift
                for i in range(0, 24):
                    errs = self.weight(s)
                    # syndrome matches error pattern
                    if errs <= w:
                        # remove errors
                        cw = cw ^ s
                        # unrotate data
                        cw = self.rotr(cw, i)
                        # count toggled bit (per Steve Duncan?)
                        if j >= 0:
                            errs += 1
                        if errs > 0 and errs <= 3:
                            tec = 1
                        # perform parity on "corrected" data
                        par_err = gl.get_parity(gl.pack(cw << 1 | parity))
                        if errs >= 3 and par_err:
                            qed = 1
                        elif par_err:
                            tec = 1
                        return (self.dissamble_cw(cw)[0], tec, qed)
                    else:
                        # rotate to next pattern
                        cw = self.rotl(cw, 1)
                        # calculate new syndrome
                        s = self.syndrome(cw)
                # toggle next trial bit
                j += 1
            else:
                if errs > 0 and errs <= 3:
                    tec = 1
                # perform parity on "corrected" data
                par_err = gl.get_parity(gl.pack(cw << 1 | parity))
                if errs >= 3 and par_err:
                    qed = 1
                elif par_err:
                    tec = 1
                return (self.dissamble_cw(cw)[0], tec, qed)
        # perform parity on "corrected" data
        par_err = gl.get_parity(gl.pack(cw << 1 | parity))
        if errs >= 3 and par_err:
            qed = 1
        elif par_err:
            tec = 1
        return (data, tec, qed)

    def assemble_cw(self, data: int, check: int):
        '''
        Creates the codeword from data and check bits as _systematic encoding_.

        Assumes `data` and `check` are represented msb to lsb.
        '''
        # print(bin(data), bin(check))
        rev_data = int('{:012b}'.format(data)[::-1], 2)
        rev_check = int('{:011b}'.format(check)[::-1], 2)
        cw = rev_data << 11 | rev_check
        return cw
    
    def dissamble_cw(self, cw: int) -> tuple:
        '''
        Disassembles a codeword back into its data and check bits.
        '''
        rev_data = cw >> 11
        rev_check = cw & 0x7ff
        data = int('{:012b}'.format(rev_data)[::-1], 2)
        check = int('{:011b}'.format(rev_check)[::-1], 2)
        return (data, check)
    
    def weight(self, cw: int):
        '''
        Calculates the weight of a 23-bit codeword (data+check).
        '''
        wgt = [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4]

        bits = 0
        k = 0

        while k < 6 and cw > 0:
            bits = bits + wgt[cw & 0xf]
            cw = cw >> 4
            k += 1
        return bits
    
    def rotl(self, cw: int, n: int):
        '''
        Rotates a 23-bit codeword cw left by n bits.
        '''
        for _ in range(0, n):
            if cw & 0x400000 != 0:
                cw = (cw << 1) | 0b1
            else:
                cw = cw << 1
        return cw & 0x7fffff
    
    def rotr(self, cw: int, n: int):
        '''
        Rotates a 23-bit codeword cw right by n bits.
        '''
        for _ in range(0, n):
            if cw & 0b1 != 0:
                cw = (cw >> 1) | 0x400000
            else:
                cw = cw >> 1
        return cw & 0x7fffff


class TestGolay(unittest.TestCase):
    '''
    Test cases for the Golay code.
    '''

    def test_codec(self):
        code = GolayCodec()

        data_tx = random.randint(0, 2**12-1)
        print('ENCODE')
        print(hex(data_tx))
        check_tx, parity_tx = code.encode(data_tx)

        print(data_tx, check_tx, parity_tx)

        packet_tx = gl.pack(parity_tx << 23 | check_tx << 12 | data_tx)
        print(packet_tx)
        num_flips = random.randint(0, 4)
        print('flips:', num_flips)
        packet_rx = gl.transmit(packet_tx, noise=num_flips)
        print(packet_rx)

        unpack = gl.unpack(packet_rx)
        data_rx = unpack & 0xfff
        check_rx = (unpack >> 12) & 0x7ff
        parity_rx = (unpack >> 23) & 0b1

        print(data_rx, check_rx, parity_rx)

        print('DECODE')
        data_rx, tec, qed = code.decode(data_rx, check_rx, parity_rx)
        print(hex(data_rx), tec, qed)
        print(data_tx, data_rx)
        if num_flips < 4:
            self.assertEqual(data_tx, data_rx)
        self.assertEqual(tec, 1 if num_flips > 0 else 0)
        self.assertEqual(qed, 1 if num_flips == 4 else 0)
