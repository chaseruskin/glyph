from hamming import HammingCodec
import hamming
import random
from verb import Logics
import cocotb
import verb as vb
from verb import Model, Constant, Signal

class HammingDec(Model):

    def __init__(self):
        self.K = Constant()

        self.code = Signal()
        self.data = Signal()
        self.sec = Signal()
        self.ded = Signal()
        super().mirror()
        self._code = HammingCodec(self.K.value)
        print('HAMMING CODE: ('+str(self._code.get_total_bits_len())+', '+str(self._code.get_data_bits_len())+')')
        self._secret = 0
        self._packet = None

    def define_coverage(self):
        from verb.coverage import CoverPoint, CoverRange

        CoverRange(
            name='code',
            goal=1,
            span=self.code.span(),
            max_steps=16,
            target=self.code
        )

        CoverPoint(
            name='single-bit error',
            goal=20,
            target=self.sec
        )

        CoverPoint(
            name='double-bit error',
            goal=20,
            target=self.ded
        )

        CoverPoint(
            name='no error',
            goal=40,
            sink=(self.sec, self.ded),
            checker=lambda sed, ded: sed.value == 0 and ded.value == 0
        )

        super().cover()

    async def setup(self):
        while vb.running():
            self._secret = Logics(random.randint(0, self.data.max()), self._code.get_data_bits_len())
            block = self._code.encode([int(i) for i in str(self._secret)][::-1])
            # print('msg (tx):', self._secret)
            # print('block (tx):', block)
            # choose some bits to flip (or none) by injecting noise
            self._packet = hamming.transmit(block, noise=random.randint(0, 2), spots=[])
            # print('block (rx):', self._packet)

            self.code.value = Logics(self._packet[::-1])

            await vb.falling_edge()

    async def model(self):
        while vb.running():
            await vb.rising_edge()
            decoding, sec, ded = self._code.decode(self._packet)
            secret = Logics(decoding[::-1], self._code.get_data_bits_len())
            # print('msg (rx):', secret)

            self.sec.value = sec
            self.ded.value = ded

            vb.assert_eq(self.data.get_handle(), secret)
            vb.assert_eq(self.sec.get_handle(), self.sec)
            vb.assert_eq(self.ded.get_handle(), self.ded)


@cocotb.test()
async def test(top):
    vb.initialize(top)

    mdl = HammingDec()
    mdl.define_coverage()

    await vb.first(
        cocotb.start_soon(mdl.setup()),
        cocotb.start_soon(mdl.model())
    )

    vb.complete()