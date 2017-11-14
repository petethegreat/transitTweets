

class tester(object):
    def __init__(self):
        self._moose = None

    @property
    def moose(self):
        ''' description of moose'''
        print('value of _moose is {m}'.format(m=self._moose))
        return self._moose

    @moose.setter
    def moose(self,value):
        print('setting of _moose to {m}'.format(m=value))
        self._moose = value

    @moose.deleter
    def moose(self):
        print('deleting _moose')
        del self._moose

