from hamming import HammingCodec

import cocotb
import verb as vb
from verb import Model, Signal, Constant, Logics

class HammingEnc(Model):

    def __init__(self):
        self.K = Constant()
        
        self.data = Signal()
        self.code = Signal()
        super().mirror()
        self._code = HammingCodec(self.K.value)
        print('HAMMING CODE: ('+str(self._code.get_total_bits_len())+', '+str(self._code.get_data_bits_len())+')')

    def define_coverage(self):
        from verb.coverage import CoverRange

        CoverRange(
            name='message range',
            span=self.data.span(),
            goal=1,
            target=self.data
        )

        super().cover()

    async def setup(self):
        while vb.running():
            self.randomize()
            await vb.falling_edge()

    async def model(self):
        while vb.running():
            await vb.rising_edge()
            msg = [int(i) for i in str(self.data.get_handle().value)]
            bits = self._code.encode(msg[::-1])
            vb.assert_eq(self.code.get_handle(), Logics(bits[::-1]))


@cocotb.test()
async def test(top):
    '''
    Tests hamming encoder.
    '''
    vb.initialize(top)

    mdl = HammingEnc()
    mdl.define_coverage()
    
    await vb.combine(
        cocotb.start_soon(mdl.setup()),
        cocotb.start_soon(mdl.model())
    )

    vb.complete()