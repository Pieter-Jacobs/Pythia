from imports import *
from rewrite.DataFrameDataset import DataFrameDataset
from rewrite.SubscriptableExample import SubscriptableExample

class Serializer:
    # Save a dataset to files
    @staticmethod
    def save_dataset(path, dataset):
        if not os.path.isdir(path):
            os.makedirs(path)
        if os.path.isfile(os.path.join(path, "examples.pkl")):
            os.remove(os.path.join(path, "examples.pkl"))
        if os.path.isfile(os.path.join(path, "fields.pkl")):
            os.remove(os.path.join(path, "fields.pkl"))
        torch.save(dataset.examples, os.path.join(
            path, "examples.pkl"), pickle_module=dill)
        torch.save(dataset.fields, os.path.join(
            path, "fields.pkl"), pickle_module=dill)

    # load a dataset from the given path
    @staticmethod
    def load_dataset(path):
        examples = torch.load(os.path.join(
            path, "examples.pkl"), pickle_module=dill)
        fields = torch.load(os.path.join(
            path, "fields.pkl"), pickle_module=dill)
        ds = DataFrameDataset(examples=examples, fields=fields)
        ds.examples.dropna(inplace=True)
        ds.examples.index = ([i for i in range(len(ds.examples))])
        return ds
