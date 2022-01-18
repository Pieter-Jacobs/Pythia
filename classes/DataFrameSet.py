from imports import *
from classes.SubscriptableExample import SubscriptableExample

class DataFrameDataset(data.Dataset):
    # initialise a dataset
    def __init__(self, fields, df=None, examples = [], is_unlabeled=False, **kwargs):
        if len(examples) == 0:
            examples = df.apply(lambda row: self.createExample(row, fields, is_unlabeled), axis = 1)
            super().__init__(examples, fields, **kwargs)
        else: 
            super().__init__(examples, fields)

    # Create example with the text and the label and a placeholder uncertainty and assigned label 
    def createExample(cls, row, fields, is_unlabeled):
        if is_unlabeled:
            row['label'] = next(iter(fields[1][1].vocab.stoi))
        return SubscriptableExample.fromlist([row['text'], row['label'], row['text'], row['text'], row['text']],  fields)

    # Sort based on length of a question
    @staticmethod
    def sort_key(ex):
        return len(ex['text'])

    #split dataset into train, val and test
    @classmethod
    def splits(cls, fields, train_df, val_df=None, test_df=None, **kwargs):
        train_data, val_data, test_data = (None, None, None)
        if train_df is not None:
            train_data = cls(df = train_df.copy(), fields = fields, **kwargs)
        if val_df is not None:
            val_data = cls(df = val_df.copy(), fields = fields, **kwargs)
        if test_df is not None:
            test_data = cls(df =test_df.copy(), fields = fields, **kwargs)

        return tuple(d for d in (train_data, val_data, test_data) if d is not None)

    def to_csv(self, file_name):
        texts = [ex.text for ex in self.examples]
        labels = [ex.label for ex in self.examples]
        pd.DataFrame(data = {'Text': texts, 'Label': labels}).to_csv(file_name)