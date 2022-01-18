from imports import *
import numpy as np


class Trainer():
    def __init__(self, model, iterator, criterion, optimizer):
        self.model = model
        self.iterator = iterator
        self.criterion = criterion
        self.optimizer = optimizer

    def train(self, n_epochs):
        print(self.iterator.dataset.examples)
        loss = []
        acc = []
        t = time.time()
        print("Starting training...")
        for epoch in range(n_epochs):
            print("Epoch number: " + str(epoch))
            train_acc, train_loss = self.training_step()
            print(
                f'\tTrain Loss: {train_loss:.3f} | Train Acc: {train_acc*100:.2f}%')
            loss.append(train_loss)
            acc.append(train_acc)
        print(f'time:{time.time()-t:.3f}')

    def training_step(self):
        epoch_loss = 0
        epoch_acc = 0
        # Tell the model it is going to be trained
        self.model.train()
        for batch in self.iterator:
            # Clear the gradients for all parameters so they don't accumulate
            self.optimizer.zero_grad()
            predictions = self.model(batch.token_ids,
                                     token_type_ids=None,
                                     attention_mask=batch.mask,
                                     labels=batch.label.long())
            loss = predictions[0]
            acc = self.compute_accuracy(predictions[1], batch.label.long())
            # Compute the loss of all parameters, make ready for backward prop
            loss.backward()
            # Update all parameters based on the gradient (backprop)
            self.optimizer.step()
            epoch_loss += float(loss.item())
            epoch_acc += float(acc)
        return epoch_acc / len(self.iterator), epoch_loss / len(self.iterator)

    def compute_accuracy(self, preds, y):
        correct = 0.0
        for i, pred in enumerate(preds):
            # Check if prediction is the same as supervised label
            if torch.tensor(np.argmax(pred.detach().cpu().numpy())) == y[i].cpu():
                correct += 1
        return correct / len(preds)

    def reset_parameters(self):
        self.model.load_state_dict(torch.load(os.path.join(
            os.getcwd(), "saves" + os.path.sep + "model.pkl")), strict=False)
        self.optimizer = AdamW(self.model.parameters(), lr=2e-5, eps=1e-8)
