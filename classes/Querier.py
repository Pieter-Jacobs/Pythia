from imports import *
import numpy as np


class Querier():
    def __init__(self, model, dataset, query_function, iterator, K, T):
        self.dispatcher = {
            'variation_ratio': self.variation_ratio,
            'predictive_entropy': self.predictive_entropy,
            'mutual_information': self.mutual_information
        }
        self.model = model
        self.dataset = dataset
        self.query_function = self.choose_query_function(query_function)
        self.iterator = iterator
        self.K = K
        self.T = T

    def sort_dataset(self, uncertainty_matrix, preds):
        self.dataset.examples.index = [
            i for i in range(len(self.dataset.examples))]
        sorted_idx = np.argsort(
            -uncertainty_matrix)
        self.dataset.examples = self.dataset.examples.reindex(
            sorted_idx)
        return preds[sorted_idx]

    def assign_uncertainties(self):
        uncertainty_matrix = []
        self.model.eval()

        # Enable dropout
        for m in self.model.modules():
            if m.__class__.__name__.startswith('Dropout'):
                m.training = True

        # Loop through the dataset and assign the uncertainties to the examples
        with torch.no_grad():
            torch.cuda.empty_cache()
            for batch in self.iterator:
                # prediction tensors
                preds = np.array([self.model(batch.token_ids,
                                             token_type_ids=None,
                                             attention_mask=batch.mask
                                             )[0].cpu().numpy() for sample in range(int(self.T))])
                preds = np.transpose(preds, (1, 0, 2))
                preds = softmax(preds, axis=2)
                # change the dataset, not the batches
                uncertainty_matrix = np.concatenate(
                    (uncertainty_matrix, self.query_function(preds)))
                sorted_preds = self.sort_dataset(uncertainty_matrix, preds)

                n = len(sorted_preds[0][0])
                avg_preds = np.array([]).reshape(0, n)
                for pred_arr in sorted_preds:
                    avg_pred = np.zeros(n)
                    for pred in pred_arr:
                        avg_pred += pred
                    avg_pred /= self.T
                    avg_pred = np.round(avg_pred * 100, 2)
                    avg_preds = np.vstack((avg_preds, avg_pred))
        return sum(uncertainty_matrix) / len(uncertainty_matrix), {str(i): {j: num for (j, num) in enumerate(pred)}
                                                                   for (i, pred) in enumerate(avg_preds)}

    def query(self):
        query_count = 0
        query_list = []
        while query_count < self.K and len(self.dataset.examples) > 0:
            query_list.append(self.dataset.examples.iloc[query_count])
            #self.dataset.examples.drop(self.dataset.examples.index[0], inplace=True)
            query_count += 1
        query_texts = {str(i): ex.text for (i, ex) in enumerate(query_list)}
        print(query_texts)
        return pd.DataFrame(data={'idx': [i for i in range(len(query_list))], 'examples': (query_list)}), query_texts

    # Handles the chosen algorithm
    def choose_query_function(self, query_function):
        while query_function not in self.dispatcher.keys():
            query_function = input('''invalid algorihm choice, try one of the following strings:
                variation_ratio
                predictive_entropy
                mutual_information\n''')
        return self.dispatcher[query_function]

    # Returns uncertainty of a prediction based on the how many times
    # the mode label was sampled with T stochastic forward passes
    def variation_ratio(self, pred_matrix):
        # chosen labels for the 10 stochastic forward passes
        preds = [preds.argmax(1) for preds in pred_matrix]
        # Determine the mode and how many times the mode whas chosen
        mode = stats.mode(preds, axis=1)
        return 1 - (mode[1].squeeze()/self.T)

    # Returns information contained in the predictive distribution
    # is highest when all classes have equal probability
    @staticmethod
    @njit
    def predictive_entropy(pred_matrix):
        n = len(pred_matrix)
        print(n)
        uncertainty_matrix = np.zeros(n)
        inner_dim = pred_matrix.shape[len(pred_matrix.shape) - 1]
        for i, preds in enumerate(pred_matrix):
            sum_ = torch.zeros(inner_dim)
            for pred in preds:
                # prevent(log(0))
                pred = np.add(pred.squeeze(
                ), 0.0000000000000000000000000000000000000000000000000000000001)
                sum_ = np.add(sum_, pred.squeeze())
            avg_preds = np.divide(sum_, len(preds))
            uncertainty_matrix[i] = -1 * \
                sum(np.multiply(avg_preds, np.log2(avg_preds)))
        return uncertainty_matrix

    # BALD function, captures the models confidence instead of the models uncertainty
    def mutual_information(self, pred_matrix):
        uncertainty_matrix = np.array([])
        inner_dim = pred_matrix.shape[len(pred_matrix.shape) - 1]
        for preds in pred_matrix:
            sum_ = torch.zeros(inner_dim)
            for pred in preds:
                # prevent log(0)
                pred = np.add(pred.squeeze(
                ), 0.0000000000000000000000000000000000000000000000000000000001)
                sum_ = np.add(sum_, np.multiply(pred, np.log2(pred)))
            uncertainty_matrix = np.append(
                uncertainty_matrix, (sum(sum_) / self.T))
        return np.add(self.predictive_entropy(pred_matrix), uncertainty_matrix)
