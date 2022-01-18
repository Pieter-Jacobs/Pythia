import numpy as np
from imports import *
from rewrite.PreProcessor import PreProcessor

class PreProcessorBert(PreProcessor):
    def __init__(self):
        super().__init__()
        self.bertTokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
        self.temp_input_ids = None

    def id_tokenizer(self, text):
        MAX_LENGTH = 30
        sentence = self.split_sentences(text)
        input_ids = self.bertTokenizer.encode(sentence, 
                truncation= True,
                max_length= MAX_LENGTH,
                add_special_tokens = True,
                return_tensors = 'pt')
        # Apply padding
        input_ids = torch.cat([input_ids.squeeze(), input_ids.new_zeros(MAX_LENGTH - input_ids.squeeze().size(0))], 0)
        self.temp_input_ids = input_ids
        return input_ids

    def mask_tokenizer(self, text):
        attention_masks = [int(token > 0) for token in self.temp_input_ids.squeeze()]
        return torch.tensor(attention_masks)

    def create_fields(self):
        TOKEN_IDS = data.Field(sequential = True, 
            batch_first = True,
            tokenize = self.id_tokenizer, 
            use_vocab=False)
        MASK = data.Field(sequential = True, 
            batch_first = True,
            tokenize = self.mask_tokenizer,
            use_vocab=False)
        return np.concatenate([super().create_fields(), [('token_ids', TOKEN_IDS) ,('mask', MASK)]])
    