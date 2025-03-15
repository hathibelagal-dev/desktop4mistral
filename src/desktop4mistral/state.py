class State:
    talk_mode = False

    @staticmethod
    def get_talk_mode():
        """
        Static method to get the value of talk_mode.
        """
        return State.talk_mode

    @staticmethod
    def set_talk_mode(value):
        """
        Static method to set the value of talk_mode.
        """
        State.talk_mode = value
