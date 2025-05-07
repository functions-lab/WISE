import numpy as np
import torch
import torch.nn.functional as F
from torch import nn



def myCrossEntropy(predList, targetList):
    batchNum = targetList.size()[0]

    loss = 0
    for batchIdx in range(batchNum):
        pred = predList[batchIdx, :]
        predSum = torch.sum(pred)
        target = targetList[batchIdx]
        loss += -torch.log(pred[target]/predSum+1e-10)
    return loss / batchNum

class Loss(nn.Module):
    def __init__(self, classNum, mode='cross'):
        super(Loss, self).__init__()

        self.classNum = classNum
        self.mode = mode

    def forward(self, pred, target):
        classNum = self.classNum
        mode = self.mode
        if mode == 'cross':
            loss = F.cross_entropy(pred, target)
        elif mode == 'cross-log':
            loss = myCrossEntropy(pred, target) # F.cross_entropy(torch.log(pred+1e-10), target)
        elif mode == 'mse':
            targetAll = F.one_hot(target, num_classes=classNum).float()
            loss = F.mse_loss(pred, targetAll)
        else:
            print('Warning: Loss Mode NOT Found!')

        return loss

class Eval(nn.Module):
    def __init__(self, classNum=10):
        super(Eval, self).__init__()
        
        self.classNum = classNum
        
    def forward(self, pred, target):
        classNum = self.classNum
        dataNum = np.shape(target)[0]
        
        mat = np.zeros((classNum, classNum))
        for dataIdx in range(dataNum):
            predMax = np.argmax(pred[dataIdx, :])
            mat[predMax, target[dataIdx]] += 1
        acc = np.trace(mat) / np.sum(mat)
        
        return acc, mat