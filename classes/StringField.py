from imports import *

class StringField(data.Field):
    def process(self, batch, device=None):
        padded = self.pad(batch)
        return padded