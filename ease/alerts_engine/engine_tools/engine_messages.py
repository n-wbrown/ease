
class scan_seq_msg:
    end_code = "END_CODE"

    def __init__(self, code=None, content=None):
        self.code = code
        self.content = content

    def __eq__(self,other):
        if type(self) == type(other):
            if self.code == other.code and self.content == other.content:
                return True 
            else:
                return False
        else:
            return False

    @property
    def end(self):
        if self.code == self.end_code:
            return True

        return False

    def set_end(self):
        self.code = self.end_code
