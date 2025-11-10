from hamming import HammingCode, send
import random
from verb.model import *
from verb import context

class HammDec:

    def __init__(self, parity_bits: int):
        self.parity_bits = parity_bits
        self._code = HammingCode(parity_bits=parity_bits)

        self.encoding = Signal(self._code.get_total_bits_len())
        self.message = Signal(self._code.get_data_bits_len())
        self.corrected = Signal()
        self.valid = Signal()

    def setup(self):
        message = Signal(self._code.get_data_bits_len())
        message.sample()
        
        encoding = self._code.encode(message.get(list)[::-1])
        # choose some bits to flip (or none) by injecting noise
        packet = send(encoding, noise=random.randint(0, 4), spots=[])

        self.encoding.set(packet[::-1])

    def eval(self):
        decoding, corrected, valid = self._code.decode(self.encoding.get(list)[::-1])
        self.message.set(decoding[::-1])
        self.corrected.set(int(corrected))
        self.valid.set(int(valid))


def main():
    mdl = HammDec(context.generic('PARITY_BITS', int))

    with vectors('inputs.txt', 'i') as inputs, vectors('outputs.txt', 'o') as outputs:
        for _ in range(1000):
            mdl.setup()
            inputs.push(mdl)
            mdl.eval()
            outputs.push(mdl)


if __name__ == '__main__':
    main()
