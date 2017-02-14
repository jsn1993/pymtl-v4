from pymtl import *

class Source(Component):

  def __init__( s ):

    s.out0 = OutPort( int )
    s.out1 = OutPort( int )

    s.data = [ (2, 1), (3, 4), (6, 5) ]

    @s.update
    def update_src():
      if s.data:
        x = s.data.pop( 0 )
        s.out0.wr( x[0] )
        s.out1.wr( x[1] )
      else:
        s.out0.wr( 0 )
        s.out1.wr( 0 )

  def line_trace( s ):
    return s.out0.line_trace() + ", " + s.out1.line_trace()

class Sink(Component):

  def __init__( s ):

    s.in0 = InPort( int )
    s.in1 = InPort( int )

    @s.update
    def update_sink():
      pass
    
  def line_trace( s ):
    return s.in0.line_trace() + ", " + s.in1.line_trace()
