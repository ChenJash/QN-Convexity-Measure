
class MyColorMap(object):
    def __init__(self) -> None:
        self.rgbs = [
            (171, 227, 246),
            # (246, 165, 172),
            # (242, 175, 175),
            (248, 182, 187),
            (185, 243, 190),
            (243, 228, 191),
            (216, 193, 246),
            (252, 245, 155),
            (221, 221, 221),
            (138, 170, 208),
            (191, 185, 134),
            # (222, 172, 172)
            (255,193,152)
        ]
        self.rgbs1 = list(map(lambda x: list(map(lambda v: v / 255, x)), self.rgbs))
    
    def colorSet(self, num):
        return self.rgbs1[:num]
