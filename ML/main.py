import argparse
import numpy as np
import matplotlib.pyplot as plt
import os
import torch.optim as optim
import torch.utils.data
from torch.utils.data import DataLoader
from tqdm import tqdm

from data import DataReader_Image, DataReader_DeepSig, DataReader_Audio
from model import ANN_Real, ANN_Comp, CNN_Comp, CNN_Std, Hybrid
from loss import Loss, Eval
from save import SaveModel



parser = argparse.ArgumentParser(description='Basic MNIST Classifier')
parser.add_argument('--data', default='MNIST', type=str, choices=['MNIST', 'FMNIST', 'SVHN', 'CIFAR-10', 'Audio', 'DeepSig'],
    help='dataset name')
parser.add_argument('--size', default=14, type=int,
    help='rescaled data size')
parser.add_argument('--dilate', default=1, type=int,
    help='dilate data size')
parser.add_argument('--type', default='zadoff', type=str, # choices=['real', 'comp', 'zadoff'],
    help='input data type')
parser.add_argument('--model', default='Hybrid', type=str, choices=['ANN-Real', 'ANN-Comp', 'CNN-Comp', 'CNN-Std', 'Hybrid'],
    help='model type')
parser.add_argument('--param', default='k200,200', type=str, help='list of model hyper-parammeters, splitted by ,')
parser.add_argument('--act', default='zadoff', type=str, choices=['zadoff', 'conv'],
    help='activation function type')
parser.add_argument('--loss', default='cross-log', type=str, choices=['cross', 'cross-log', 'mse'],
    help='loss function type')
parser.add_argument('--epoch', default=100, type=int, help='train epoch number')
parser.add_argument('--batch', default=32, type=int, help='batch size')
parser.add_argument('--device', default='gpu', type=str, help='running device')
parser.add_argument('--token', default='test', type=str, help='training token')



if __name__ == '__main__':
    opt = parser.parse_args()
    DATA = opt.data
    SIZE = opt.size
    DILATE = opt.dilate
    TYPE = opt.type
    MODEL = opt.model
    PARAM = opt.param
    ACT = opt.act
    LOSS = opt.loss
    EPOCH = opt.epoch
    BATCH = opt.batch
    DEVICE = opt.device
    TOKEN = opt.token

    trainCache = './Data/Data_'+DATA+'_'+TYPE+'_s'+str(SIZE)+'_d'+str(DILATE)+'_train.pt'
    testCache = './Data/Data_'+DATA+'_'+TYPE+'_s'+str(SIZE)+'_d'+str(DILATE)+'_test.pt'
    if os.path.exists(trainCache) and os.path.exists(testCache):
        trainSet = torch.load(trainCache)
        testSet = torch.load(testCache)
    else:
        if DATA in ['MNIST', 'FMNIST', 'SVHN', 'CIFAR-10']:
            trainSet = DataReader_Image(dataset=DATA, phase='train', imageSize=SIZE, type=TYPE)
            testSet = DataReader_Image(dataset=DATA, phase='test', imageSize=SIZE, type=TYPE)
        elif DATA == 'Audio':
            trainSet = DataReader_Audio(dataPath='./Data/AudioMNIST/train_new/', waveLen=24000, ratio=24000//SIZE, type=TYPE)
            testSet = DataReader_Audio(dataPath='./Data/AudioMNIST/test_new/', waveLen=24000, ratio=24000//SIZE, type=TYPE)
        elif DATA == 'DeepSig':
            trainSet = DataReader_DeepSig(dataPath='./Data/DeepSig/', waveLen=SIZE, span=[0, 0.9], type=TYPE,
                moduSet=list(range(24)), snrSet=[30])
            testSet = DataReader_DeepSig(dataPath='./Data/DeepSig/', waveLen=SIZE, span=[0.9, 1.0], type=TYPE,
                moduSet=list(range(24)), snrSet=[30])
        torch.save(trainSet, trainCache)
        torch.save(testSet, testCache)
        testSet.SaveData('./Data/Data_'+DATA+'_'+TYPE+'_'+str(SIZE)+'.mat')
    dataShape, classNum = testSet.GetShape()
    trainLoader = DataLoader(dataset=trainSet, num_workers=0, batch_size=BATCH, shuffle=True)
    testLoader = DataLoader(dataset=testSet, num_workers=0, batch_size=1, shuffle=False)

    resultPath = './Result/'+DATA+'_size' + str(SIZE) + '_' + TOKEN + '/'
    if not os.path.exists(resultPath):
        os.makedirs(resultPath)

    device = torch.device('cuda' if torch.cuda.is_available() and DEVICE=='gpu' else 'cpu')

    if MODEL in ['ANN-Real', 'ANN-COMP']:
        hiddenList = [int(param) for param in PARAM.split(',')]
        if any([hidden < 0 for hidden in hiddenList]):
            hiddenList = []

        if MODEL == 'ANN-Real':
            if not TYPE in ['real']:
                print('Warning: Data Type and Model Type Mismatched!')
            ClassifierModel = ANN_Real(dataShape=dataShape, classNum=classNum, hiddenList=hiddenList)
        elif MODEL == 'ANN-Comp':
            if not TYPE in ['comp', 'zadoff']:
                print('Warning: Data Type and Model Type Mismatched!')
            ClassifierModel = ANN_Comp(dataShape=dataShape, classNum=classNum, hiddenList=hiddenList, act=ACT)
        else:
            print('Warning: Model Type NOT Found!')
    if MODEL in ['ANN-Real', 'ANN-COMP']:
        kernelList = [int(param) for param in PARAM.split(',')]
        if any([kernel < 0 for kernel in kernelList]):
            kernelList = []

        if MODEL == 'CNN-Comp':
            if not TYPE in ['comp', 'zadoff']:
                print('Warning: Data Type and Model Type Mismatched!')
            ClassifierModel = CNN_Comp(dataShape=dataShape, classNum=classNum, kernelList=kernelList, act=ACT)
        elif MODEL == 'CNN-Std':
            if not TYPE in ['comp', 'zadoff']:
                print('Warning: Data Type and Model Type Mismatched!')
            ClassifierModel = CNN_Std(dataShape=dataShape, classNum=classNum, kernelList=kernelList, act=ACT)
        else:
            print('Warning: Model Type NOT Found!')
    elif MODEL == 'Hybrid':
        kernelList = []
        hiddenList = []
        window = -1
        if len(PARAM) > 0:
            for param in PARAM.split(','):
                if param[0] == 'k':
                    kernelList.append(int(param[1:]))
                elif param[0] == 'h':
                    hiddenList.append(int(param[1:]))
                else:
                    window = int(param)
        
        if(not TYPE in ['comp', 'zadoff'])and('stft-zadoff' not in TYPE):
            print('Warning: Data Type and Model Type Mismatched!')
        ClassifierModel = Hybrid(dataShape=dataShape, classNum=classNum, kernelList=kernelList, window=window, hiddenList=hiddenList, act=ACT)
    else:
        print('Warning: Model Type NOT Found!')
    print('Model parameter number:', [param.size() for param in ClassifierModel.parameters()], \
        'Total:', sum(param.numel() for param in ClassifierModel.parameters()))
    optimizer = optim.Adam(ClassifierModel.parameters(), lr=1e-3)
    
    ClassifierLoss = Loss(classNum=classNum, mode=LOSS)
    ClassifierEval = Eval(classNum=classNum)    

    ClassifierModel.to(device)
    ClassifierLoss.to(device)

    resultList = {
        'lossTrain': [], 'accTrain': [], 'matTrain': [], 
        'lossTest': [], 'accTest': [], 'matTest': []}
    lossMin = +np.inf
    accMax = -np.inf
    for epochIdx in range(EPOCH):
        
        # Model Training
        ClassifierModel.train()
        result = {'dataNum': 0, 'loss': 0, 'acc': 0, 'mat': np.zeros((classNum, classNum))}
        trainBar = tqdm(trainLoader)
        for target, data in trainBar:
            dataNum = target.size(0)
            result['dataNum'] += dataNum

            data = data.to(device)
            
            optimizer.zero_grad()
            pred = ClassifierModel(data)
            loss = ClassifierLoss(pred, target)
            acc, mat = ClassifierEval(
                pred.detach().cpu().numpy(), 
                target.detach().cpu().numpy())
            loss.backward()
            optimizer.step()
            
            result['loss'] += loss.item() * dataNum
            result['acc'] += acc * dataNum
            result['mat'] += mat

            trainBar.set_description(desc='[%d/%d] Loss: %.4f Acc: %.4f'
                % (epochIdx, EPOCH,
                result['loss'] / result['dataNum'],
                result['acc'] / result['dataNum']))
        resultList['lossTrain'].append(result['loss']/result['dataNum'])
        resultList['accTrain'].append(result['acc']/result['dataNum'])
        resultList['matTrain'].append(result['mat'])
        
        # Model Testing
        ClassifierModel.eval()
        result = {'dataNum': 0, 'loss': 0, 'acc': 0, 'mat': np.zeros((classNum, classNum))}
        testBar = tqdm(testLoader)
        for target, data in testBar:
            dataNum = target.size(0)
            result['dataNum'] += dataNum

            data = data.to(device)
            
            pred = ClassifierModel(data)
            loss = ClassifierLoss(pred, target)
            acc, mat = ClassifierEval(
                pred.detach().cpu().numpy(), 
                target.detach().cpu().numpy())
            
            result['loss'] += loss.item() * dataNum
            result['acc'] += acc * dataNum
            result['mat'] += mat

            testBar.set_description(desc='[%d/%d] Loss: %.4f Acc: %.4f'
                % (epochIdx, EPOCH,
                result['loss'] / result['dataNum'],
                result['acc'] / result['dataNum']))
        resultList['lossTest'].append(result['loss']/result['dataNum'])
        resultList['accTest'].append(result['acc']/result['dataNum'])
        resultList['matTest'].append(result['mat'])

        # Model Saving
        epochAxis = np.arange(0, epochIdx+1)
        
        fig, ax = plt.subplots()
        ax.plot(epochAxis, resultList['lossTrain'])
        ax.plot(epochAxis, resultList['lossTest'])
        fig.savefig(resultPath + 'loss.png')
        plt.close(fig)
        
        fig, ax = plt.subplots()
        ax.plot(epochAxis, resultList['accTrain'])
        ax.plot(epochAxis, resultList['accTest'])
        fig.savefig(resultPath + 'acc.png')
        plt.close(fig)

        resultList = SaveModel(path=resultPath, token='last', Model=ClassifierModel, resultIn=resultList, isMat=False, isModel=False)
        if accMax < resultList['accTest'][-1]:
            accMax = resultList['accTest'][-1]
            resultList = SaveModel(path=resultPath, token='accMax', Model=ClassifierModel, resultIn=resultList, isMat=True, isModel=False)    
        if lossMin > resultList['lossTest'][-1]:
            lossMin = resultList['lossTest'][-1]
            resultList = SaveModel(path=resultPath, token='lossMin', Model=ClassifierModel, resultIn=resultList, isMat=True, isModel=False)
