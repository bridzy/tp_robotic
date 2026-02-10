class RobotMobile:
    def __init__(self, x=0.0, y=0.0, orientation=0.0):
        self.x = float(x)
        self.y = float(y)
        self.orientation = float(orientation)  # radians

    def afficher(self):
        print(f"RobotMobile(x={self.x:.3f}, y={self.y:.3f}, orientation={self.orientation:.3f} rad)")