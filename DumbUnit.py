from pymtl import *
from MinMaxUnit import MinMaxUnit

class DumbUnit(Component):

  def __init__( s, typ ):

    s.mmu  = MinMaxUnit( typ )

    s.in0  = InPort( typ )
    s.in1  = InPort( typ )
    
    s.connect( s.in0, s.mmu.in0 )
    s.connect( s.in1, s.mmu.in1 )

    s.out0 = OutPort( typ )
    s.out1 = OutPort( typ )

    s.connect( s.out0, s.mmu.out0 )
    s.connect( s.out1, s.mmu.out1 )


  def line_trace( s ):
    return s.out0.line_trace() + ", " + s.out1.line_trace()
