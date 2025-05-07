import argparse
import mat73
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.io import loadmat, savemat
import torch.optim as optim
import torch.utils.data
from torch.utils.data import DataLoader
from torch.utils.data.dataset import Dataset
from tqdm import tqdm



parser = argparse.ArgumentParser(description='Machine Learning for Calibration')
parser.add_argument('--input', default=300, type=int,
    help='Size of input vector')
parser.add_argument('--output', default=10, type=int,
    help='Size of the output vector')
parser.add_argument('--scalar', default=1, type=float,
    help='Scalar to normalize the output')
parser.add_argument('--ratio', default=0.1, type=float,
    help='Ratio of testing set over all the dataset')
parser.add_argument('--model', default='one', type=str, choices=['four', 'one', 'init', 'real', 'small', 'fft'],
    help='Linear model from input to output')
parser.add_argument('--epoch', default=20, type=int, help='train epoch number')
parser.add_argument('--batch', default=64, type=int, help='batch size')
parser.add_argument('--device', default='gpu', type=str, help='running device')
parser.add_argument('--token', default='', type=str, help='training token')



class DataReader(Dataset):
    def __init__(self, dataPath, inputSize, outputSize, span=[0, 1], token=''):
        super(DataReader, self).__init__()
        
        dataDictIn = mat73.loadmat(dataPath+'dataIn_'+str(inputSize)+'_'+str(outputSize)+'.mat')
        inputAll = dataDictIn['inputAll']
        weightAll = dataDictIn['weightAll']
        if weightAll.ndim == 2:
            weightAll = weightAll[:, :, np.newaxis]
        if token != '':
            dataDictOut = loadmat(dataPath+'dataOut_'+str(inputSize)+'_'+str(outputSize)+'_'+token+'.mat')
        else:
            dataDictOut = loadmat(dataPath+'dataOut_'+str(inputSize)+'_'+str(outputSize)+'.mat')
        outputAll = dataDictOut['outputAnalAll']
        
        testNum = np.shape(outputAll)[0]
        startIdx = int(span[0]*testNum)
        endIdx = int(span[1]*testNum)
        self.inputList = []
        self.weightList = []
        self.outputList = []
        for dataIdx in range(startIdx, endIdx):
            if not np.isnan(outputAll[dataIdx, :]).any():
                self.inputList.append(inputAll[dataIdx, :])
                self.weightList.append(weightAll[dataIdx, :, :])
                self.outputList.append(outputAll[dataIdx, :])
            else:
                print('Warning: Bad Data at '+str(dataIdx+1))

    def __getitem__(self, index):
        input_ = self.inputList[index]
        weight = self.weightList[index]
        output = self.outputList[index]

        inputTensor = torch.from_numpy(input_)
        weightTensor = torch.from_numpy(weight)
        outputTensor = torch.tensor(output)
        return inputTensor, weightTensor, outputTensor # no .float()?

    def __len__(self):
        return len(self.inputList)

if __name__ == '__main__':
    opt = parser.parse_args()
    INPUT = opt.input
    OUTPUT = opt.output
    SCALAR = opt.scalar * INPUT * INPUT * OUTPUT
    RATIO = opt.ratio
    MODEL = opt.model
    EPOCH = opt.epoch
    BATCH = opt.batch
    DEVICE = opt.device
    TOKEN = opt.token

    colorSet = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    torch.random.manual_seed(0)

    dataPath = './dataset/'
    if TOKEN != '':
        resultPath = './Result/result_' + str(INPUT) + '_' + str(OUTPUT) + '_' + MODEL + '_' + TOKEN + '/'
    else:
        resultPath = './Result/result_' + str(INPUT) + '_' + str(OUTPUT) + '_' + MODEL + '/'
    if not os.path.exists(resultPath):
        os.mkdir(resultPath)

    trainSet = DataReader(dataPath=dataPath, inputSize=INPUT, outputSize=OUTPUT, span=[0, 1-RATIO], token=TOKEN)
    trainLoader = DataLoader(dataset=trainSet, num_workers=4, batch_size=BATCH, shuffle=True)
    trainNum = trainSet.__len__()
    testSet = DataReader(dataPath=dataPath, inputSize=INPUT, outputSize=OUTPUT, span=[1-RATIO, 1], token=TOKEN)
    testLoader = DataLoader(dataset=testSet, num_workers=4, batch_size=1, shuffle=False)
    testNum = testSet.__len__()

    device = torch.device('cuda' if torch.cuda.is_available() and DEVICE=='gpu' else 'cpu')

    if MODEL == 'four':
        alpha = torch.randn((INPUT, OUTPUT), dtype=torch.cfloat, requires_grad=True)
        beta = torch.randn((INPUT, OUTPUT), dtype=torch.cfloat, requires_grad=True)
        gamma = torch.randn((INPUT, OUTPUT), dtype=torch.cfloat, requires_grad=True)
        delta = torch.randn((OUTPUT), dtype=torch.cfloat, requires_grad=True)
        optimizer = optim.Adam([alpha, beta, gamma, delta], lr=1e-2)
        alpha.to(device)
        beta.to(device)
        gamma.to(device)
        delta.to(device)
    elif MODEL == 'one':
        alpha = torch.randn((INPUT, OUTPUT), dtype=torch.cfloat, requires_grad=True)
        beta = torch.zeros((INPUT, OUTPUT), dtype=torch.cfloat)
        gamma = torch.zeros((INPUT, OUTPUT), dtype=torch.cfloat)
        delta = torch.zeros((OUTPUT), dtype=torch.cfloat)
        optimizer = optim.Adam([alpha], lr=1e-2)
        alpha.to(device)
    elif MODEL == 'init':
        alpha = torch.ones((INPUT, OUTPUT), dtype=torch.cfloat, requires_grad=True)
        beta = torch.zeros((INPUT, OUTPUT), dtype=torch.cfloat)
        gamma = torch.zeros((INPUT, OUTPUT), dtype=torch.cfloat)
        delta = torch.zeros((OUTPUT), dtype=torch.cfloat)
        optimizer = optim.Adam([alpha], lr=1e-2)
        alpha.to(device)
    elif MODEL == 'real':
        alpha = torch.ones((INPUT, OUTPUT), requires_grad=True)
        beta = torch.zeros((INPUT, OUTPUT), dtype=torch.cfloat)
        gamma = torch.zeros((INPUT, OUTPUT), dtype=torch.cfloat)
        delta = torch.zeros((OUTPUT), dtype=torch.cfloat)
        optimizer = optim.Adam([alpha], lr=1e-2)
        alpha.to(device)
    elif MODEL == 'small':
        alpha = torch.randn((INPUT), requires_grad=True)
        beta = torch.zeros((INPUT, OUTPUT))
        gamma = torch.zeros((INPUT, OUTPUT))
        delta = torch.zeros((OUTPUT))
        optimizer = optim.Adam([alpha], lr=1e-2)
        alpha.to(device)
    elif MODEL == 'fft':
        # Not Available Yet
        freq = torch.randn((INPUT), requires_grad=True).to(device)
    
    resultList = {
        'lossTrain': [], 'lossTest': []}
    lossMin = +np.inf
    for epochIdx in range(EPOCH):
        trainBar = tqdm(trainLoader)
        outputEstMat = np.nan * np.ones((OUTPUT, trainNum), dtype=np.cfloat)
        outputGtMat = np.nan * np.ones((OUTPUT, trainNum), dtype=np.cfloat)
        dataNum = 0
        lossAll = 0
        for input_, weight, output in trainBar:
            batchNum = input_.size(0)

            optimizer.zero_grad()

            loss = 0
            for batchIdx in range(batchNum):
                for outputIdx in range(OUTPUT):
                    if MODEL in ['four', 'one', 'init', 'real']:
                        predVec = alpha[:, outputIdx]*weight[batchIdx, :, outputIdx]*input_[batchIdx, :] + \
                            beta[:, outputIdx]*weight[batchIdx, :, outputIdx] + \
                            gamma[:, outputIdx]*input_[batchIdx, :] + delta[outputIdx]
                    elif MODEL in ['small']:
                        predVec = alpha*weight[batchIdx, :, outputIdx]*input_[batchIdx, :]
                    predSum = torch.sum(predVec, axis=-1)
                    labelSum = output[batchIdx, outputIdx]*SCALAR
                    loss += (torch.abs(predSum) - torch.abs(labelSum)) ** 2
                    
                    outputEstMat[outputIdx, dataNum] = predSum.item()
                    outputGtMat[outputIdx, dataNum] = labelSum.item()
                dataNum += 1

            loss.backward()
            optimizer.step()

            lossAll += loss.item()
            trainBar.set_description(desc='[%d/%d] RMSE: %.4f'
                % (epochIdx, EPOCH, np.sqrt(lossAll/dataNum/OUTPUT)))
        resultList['lossTrain'].append(np.sqrt(lossAll/dataNum/OUTPUT))
        
        fig, ax = plt.subplots()
        for outputIdx in range(OUTPUT):
            ax.scatter(np.abs(outputGtMat[outputIdx, :]), np.abs(outputEstMat[outputIdx, :]), \
                c=colorSet[outputIdx%len(colorSet)])
        ax.plot([0, np.sqrt(INPUT)], [0, np.sqrt(INPUT)])
        ax.set_xlabel('Analog Computing')
        # ax.set_xlim(left=0, right=np.sqrt(INPUT))
        ax.set_ylabel('Digital Computing')
        # ax.set_ylim(bottom=0, top=np.sqrt(INPUT))
        ax.set_title('EPOCH: '+str(epochIdx)+' RMSE: '+str(np.sqrt(lossAll/dataNum/OUTPUT)))
        fig.savefig(resultPath+'result_train_'+str(epochIdx)+'.png')
        # fig.savefig(resultPath+'result_train.png')
        plt.close(fig)

        with torch.no_grad():
            testBar = tqdm(testLoader)
            outputEstMat = np.nan * np.ones((OUTPUT, testNum), dtype=np.cfloat)
            outputGtMat = np.nan * np.ones((OUTPUT, testNum), dtype=np.cfloat)
            dataNum = 0
            lossAll = 0
            for input_, weight, output in testBar:
                batchNum = input_.size(0)
                
                loss = 0
                for batchIdx in range(batchNum):
                    for outputIdx in range(OUTPUT):
                        if MODEL in ['four', 'one', 'init', 'real']:
                            predVec = alpha[:, outputIdx]*weight[batchIdx, :, outputIdx]*input_[batchIdx, :] + \
                                beta[:, outputIdx]*weight[batchIdx, :, outputIdx] + \
                                gamma[:, outputIdx]*input_[batchIdx, :] + delta[outputIdx]
                        elif MODEL in ['small']:
                            predVec = alpha*weight[batchIdx, :, outputIdx]*input_[batchIdx, :]
                        predSum = torch.sum(predVec, axis=-1)
                        labelSum = output[batchIdx, outputIdx]*SCALAR
                        loss += (torch.abs(predSum) - torch.abs(labelSum)) ** 2
                        
                        outputEstMat[outputIdx, dataNum] = predSum.item()
                        outputGtMat[outputIdx, dataNum] = labelSum.item()
                    dataNum += 1

                lossAll += loss.item()
                testBar.set_description(desc='[%d/%d] RMSE: %.4f'
                    % (epochIdx, EPOCH, np.sqrt(lossAll/dataNum/OUTPUT)))
            resultList['lossTest'].append(np.sqrt(lossAll/dataNum/OUTPUT))

            fig, ax = plt.subplots()
            ax.plot(np.arange(0, epochIdx+1), resultList['lossTrain'])
            ax.plot(np.arange(0, epochIdx+1), resultList['lossTest'])
            fig.savefig(resultPath + 'loss.png')
            plt.close(fig)

            fig, ax = plt.subplots()
            for outputIdx in range(OUTPUT):
                ax.scatter(np.abs(outputGtMat[outputIdx, :]), np.abs(outputEstMat[outputIdx, :]), \
                    c=colorSet[outputIdx%len(colorSet)])
            ax.plot([0, np.sqrt(INPUT)], [0, np.sqrt(INPUT)])
            ax.set_xlabel('Analog Computing')
            # ax.set_xlim(left=0, right=np.sqrt(INPUT))
            ax.set_ylabel('Digital Computing')
            # ax.set_ylim(bottom=0, top=np.sqrt(INPUT))
            ax.set_title('EPOCH: '+str(epochIdx)+' RMSE: '+str(np.sqrt(lossAll/dataNum/OUTPUT)))
            fig.savefig(resultPath+'result_test_'+str(epochIdx)+'.png')
            # fig.savefig(resultPath+'result_test.png')
            plt.close(fig)

            if lossAll < lossMin:
                lossMin = lossAll
                alphaMat = alpha.detach().cpu().numpy()
                if MODEL in ['small']:
                    alphaMat = np.repeat(alphaMat[:, np.newaxis], OUTPUT, axis=1)
                savemat(resultPath+'result.mat', { \
                    'alphaMat': alphaMat,
                    'betaMat': beta.detach().cpu().numpy(),
                    'gammaMat': gamma.detach().cpu().numpy(),
                    'deltaMat': delta.detach().cpu().numpy()})