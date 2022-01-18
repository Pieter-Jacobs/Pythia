import numpy as np
from imports import *
from rewrite.DataFrameSet import DataFrameDataset
from rewrite.StringField import StringField

class PreProcessor():
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    # Pre process the dataframe into a generalised format
    def pre_process(self, df, selected_columns):
        df = self.drop_columns(df, selected_columns)
        df = self.rename_columns(df, selected_columns)
        #df['text'] = df['text'].apply(
        #    lambda text: self.remove_non_ascii(text))
        df = self.remove_empty_strings(df)
        print(df)
        return df

    # Generalise the header names of the dataframe to 'text' and 'label'
    def rename_columns(self, df, columns):
        df.columns = ['text', 'label'] if columns[0] < columns[1] else ['label', 'text']
        return df

    # Drop the columns that the user did not select
    def drop_columns(self, df, columns):
        cols_to_drop = [df.columns[col] for col in range(len(df.columns)) if col not in columns]
        df.drop(columns=cols_to_drop, axis=1, inplace=True)
        return df
        
    # Remove any non printable charcters
    def remove_non_ascii(self, text):
        filter(lambda x: x in string.printable, text)
        return text
    
    # Tokenize a string with spacy
    def tokenizer(self, text):
        sentence = self.split_sentences(text)
        return sentence

    # Remove empty strings from the df
    def remove_empty_strings(self, df):
        return df.loc[df['text'].str.len() > 0]

    # Splits the dataset into a labeled part and an unlabeled part
    def split_labeled_unlabeled(self, df):
        df_labeled = df[df['label'].notnull()]
        df_unlabeled = df[df['label'].isnull()]
        print(df_unlabeled)
        # Reindex the two data sets
        df_labeled.index = ([i for i in range(len(df_labeled))])
        df_unlabeled.index = ([i for i in range(len(df_unlabeled))])
        return df_labeled, df_unlabeled

    # use nltk to split the sentences
    def split_sentences(self,text):
        return tokenize.sent_tokenize(text)[0]

    # Create the necassary fields for a normal classification task
    def create_fields(self):
        TEXT = StringField(sequential = True, 
            batch_first = True,
            tokenize = self.tokenizer, 
            use_vocab=False)
        LABEL = data.LabelField(dtype = torch.float)
        return  [('text', TEXT), ('label', LABEL)]
        
    # Build the dataframesets
    def create_datasets(self, df):
        df_labeled, df_unlabeled = self.split_labeled_unlabeled(df)
        fields = self.create_fields()
        train_ds = DataFrameDataset(fields, df_labeled)
        # Build a mapping to numerical labels
        # We do this before building the unlabeled dataset
        # so we can use a placeholder label from the train datasets
        fields[1][1].build_vocab(train_ds)
        unlabeled_ds = DataFrameDataset(
            fields, df_unlabeled, is_unlabeled=True)
        return train_ds, unlabeled_ds, fields[1][1].vocab.stoi
