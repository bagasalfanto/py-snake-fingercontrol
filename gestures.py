class GestureRecognizer:
    """Gesture ringan berbasis landmark tangan, cukup stabil untuk demo game."""

    FINGER_TIPS = [8, 12, 16, 20]
    FINGER_PIPS = [6, 10, 14, 18]

    def classify(self, hand) -> str | None:
        extended = [
            hand[tip].y < hand[pip].y - 0.025
            for tip, pip in zip(self.FINGER_TIPS, self.FINGER_PIPS)
        ]
        count = sum(extended)

        if count >= 4:
            return "PALM"
        if count == 0:
            return "FIST"
        if extended[0] and extended[1] and not extended[2] and not extended[3]:
            return "TWO_FINGERS"
        return None
