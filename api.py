from imports import *
from flask import Flask
from flask import request
from flask import jsonify
from flask import send_file
from flask_cors import CORS
from rewrite.Trainer import Trainer
from rewrite.PreProcessorSBert import PreProcessorSBert
from rewrite.ActiveLearner import ActiveLearner
from rewrite.Querier import Querier
import json
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app)

hyperparameters = {
    'T': 10,
    'K': 10,
}

dict = {
    'labeled': None,
    'unlabeled': None,
    'label_mapping': None,
    'model': None,
    'active-learner': None,
    'device': torch.device(
        'cuda' if torch.cuda.is_available() else 'cpu'),
    'queried': None
}


def assign_label(ex, label):
    ex.label = label
    return ex


@app.route('/api/preprocess', methods=['POST', 'GET'])
def preprocess():
    if request.method == 'POST':
        json = request.get_json()
        preProcessor = PreProcessorSBert()
        df = preProcessor.pre_process(pd.DataFrame(
            json['file']).loc[0:100], json['columns'])
        seed_ds, unlabeled_ds, label_map = preProcessor.create_datasets(df)
        dict['labeled'] = seed_ds
        dict['unlabeled'] = unlabeled_ds
        dict['label_mapping'] = label_map

        dict['model'] = BertForSequenceClassification.from_pretrained(
            # Use the 12-layer BERT model, with an uncased vocab.
            "bert-base-uncased",
            num_labels=len(label_map),
            output_attentions=False,
            output_hidden_states=False
        )
        dict['model'].to(dict['device'])
    return 'Done'


@app.route('/api/init_model', methods=['PUT'])
def init_model():
    if 'model' in request.files.keys():
        file = request.files['model']
        dict['model'].load_state_dict(torch.load(file), strict=False)
    iterator = data.BucketIterator(
        dataset=dict['labeled'],
        batch_size=128,
        device=dict['device']
    )
    query_iterator = data.BucketIterator(
        dataset=dict['unlabeled'],
        batch_size=len(dict['unlabeled']),
        sort_within_batch=False,
        sort=False,
        shuffle=False,
        device=dict['device']
    )
    trainer = Trainer(
        model=dict['model'],
        criterion=nn.CrossEntropyLoss(),
        optimizer=AdamW(dict['model'].parameters(), lr=2e-5, eps=1e-8),
        iterator=iterator,
    )
    querier = Querier(
        model=dict['model'],
        dataset=dict['unlabeled'],
        query_function='variation_ratio',
        iterator=query_iterator,
        T=hyperparameters['T'],
        K=hyperparameters['K']
    )
    torch.save(dict['model'].state_dict(), os.path.join(
        os.getcwd(), "saves" + os.path.sep + "model.pkl"))
    dict['active-learner'] = ActiveLearner(dict['model'],
                                           dict['unlabeled'], dict['labeled'], trainer, querier)
    return 'Done'


@app.route('/api/save_model_to_file', methods=['PUT'])
def save_model_to_file():
    json = request.get_json()
    filename = json['filename'] + '.pkl'
    torch.save(dict['model'].state_dict(), os.path.join(
        os.getcwd(), "saves" + os.path.sep + filename))
    return "Done"


@app.route('/api/delete_model', methods=['PUT'])
def delete_model():
    del dict['model']
    return "Done"

    
@app.route('/api/classify_unlabeled_data', methods=['PUT'])
def classify_unlabeled_data():
    dict['labeled'] = dict['active-learner'].classify_dataset()
    get_labeled_csv()
    return 'Done'

@app.route('/api/get_labeled_csv', methods=['GET'])
def get_labeled_csv():
    try:
        dict['labeled'].to_csv("labeled_dataset.csv")
        return send_file("labeled_dataset.csv",
                         mimetype='csv/text',
                         attachment_filename='dataset.csv',
                         as_attachment=True, cache_timeout=0)
    except Exception as e:
        return str(e)


@app.route('/api/label_examples', methods=['POST'])
def label_examples():
    json = request.get_json()
    labels = json['labels']
    dict['queried'] = dict['queried'].apply(lambda row: assign_label(
        row.loc['examples'], labels[row.loc['idx']]), axis=1)
    dict['unlabeled'].examples.drop(
        index=[i for i in range(hyperparameters['K'])], inplace=True)
    dict['labeled'].examples = dict['labeled'].examples.append(
        dict['queried'], ignore_index=True)
    return "Done"


@app.route('/api/get_label_mapping', methods=['GET'])
def get_label_mapping():
    return dict['label_mapping']


@app.route('/api/take_al_step', methods=['GET'])
def take_al_step():
    examples, texts, uncertainty, preds = dict['active-learner'].step()
    dict['queried'] = examples
    return jsonify(texts=texts, uncertainty=uncertainty, preds=preds)


if __name__ == '__main__':
    app.run()
