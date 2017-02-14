from pymtl import *

class MinMaxUnit(Component):

  def __init__( s, typ ):

    s.in0  = InPort( typ )
    s.in1  = InPort( typ )

    s.out0 = OutPort( typ )
    s.out1 = OutPort( typ )

    @s.update
    def update_add():
      s.out0.wr( min( s.in0.rd(), s.in1.rd() ) )
      s.out1.wr( max( s.in0.rd(), s.in1.rd() ) )

  def line_trace( s ):
    return s.out0.line_trace() + ", " + s.out1.line_trace()
