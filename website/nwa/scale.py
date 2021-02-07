class Scale:
    """
    Rescale numbers, see D3js scale object.
    Intended use::
        s = Scale(domain=[1, 100],
                  range=[0, 1])
        s.linear(50)  # -> 0.5
    """

    def __init__(self, domain, range=(0, 1)):
        self.domain = domain
        self.range = range

    def linear(self, a):
        """
        Linear scale.
        """
        if max(self.domain) - min(self.domain) == 0:
            return 0
        
        mx = float(
            (max(self.range) - min(self.range))) \
            / (max(self.domain) - min(self.domain))
        return mx * (a - min(self.domain)) + min(self.range)

    def linear_inv(self, a):
        """
        Inverted linear scale.
        """
        return float(max(self.range) - self.linear(a))
