from imports import *
import numpy as np

class ActiveLearner():
    def __init__(self, model, unlabeled_ds, labeled_ds, trainer, querier = None):
        self.model = model
        self.labeled_ds = labeled_ds
        self.unlabeled_ds = unlabeled_ds
        self.trainer = trainer
        self.querier = querier

    def step(self):
        self.trainer.reset_parameters()
        self.trainer.train(5)
        uncertainty, avg_preds = self.querier.assign_uncertainties()
        examples, texts = self.querier.query()
        return examples, texts, uncertainty, avg_preds

    def classify_dataset(self):
        label_mapping = self.labeled_ds.fields['label'].vocab.stoi
        label_mapping = {y:x for x,y in label_mapping.items()}
        print(label_mapping)
        self.model.eval()
        for i in range(len(self.unlabeled_ds.examples)):
            ex = self.unlabeled_ds.examples[i]
            print(ex.token_ids)
            ex.token_ids = ex.token_ids.reshape(1, len(ex.token_ids)).to(torch.device('cuda'))
            print(ex.token_ids)
            ex.mask = ex.mask.reshape(1, len(ex.mask)).to(torch.device('cuda'))
            pred = self.model(ex.token_ids, attention_mask=ex.mask)
            ex.label = label_mapping[np.argmax(pred[0].detach().cpu().numpy())]
        self.labeled_ds.examples = self.labeled_ds.examples.append(self.unlabeled_ds.examples)
        return self.labeled_ds