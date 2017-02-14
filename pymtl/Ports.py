class InPort:

  def __init__( s, typ ): pass

  def rd( s ): pass

  def __call__( s ):
    return rd()

  def line_trace( s ):
    return str(s.rd())

  # no wr method because an InPort is required to connect to an OutPort

class OutPort:

  def __init__( s, typ ):
    s.var   = typ()

  def rd( s ):
    return s.var

  def wr( s, v ):
    s.var = v

  def __call__( s ):
    return rd()

  def line_trace( s ):
    return str(s.var)
