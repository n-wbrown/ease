import datetime

class scan_seq_msg:
    end_code = "END_CODE"
    i_last_change = None
    
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
    
    def _get_code(self):
        return self._code

    def _set_code(self, value):
        self._code = value
        self._last_change = datetime.datetime.now()

    def _del_code(self):
        del self._code
        self._last_change = datetime.datetime.now()

    def _get_content(self):
        return self._content

    def _set_content(self, value):
        self._content = value
        self._last_change = datetime.datetime.now()

    def _del_content(self):
        del self._content
        self._last_change = datetime.datetime.now()

    code = property(_get_code, _set_code, _del_code)

    content = property(_get_content, _set_content, _del_code)

    @property
    def last_change(self):
        return self._last_change

    

    @property
    def end(self):
        if self.code == self.end_code:
            return True

        return False

    def set_end(self):
        self.code = self.end_code
