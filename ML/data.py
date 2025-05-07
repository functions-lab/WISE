import csv
import numpy as np
import os
import pickle
from scipy.io import loadmat, savemat
import soundfile as sf
import torch
from torch.utils.data.dataset import Dataset
from tqdm import tqdm

import general



def LoadData_MNIST(dataPath):
    targetList = []
    imageList = []
    with open(dataPath, mode='r') as dataCSV:
        lineList = list(csv.reader(dataCSV))
        for line in tqdm(lineList, desc='Loading'):
            target = int(line[0])
            targetList.append(target)
            image = np.reshape(np.array([int(pixel) for pixel in line[1:]]), (28, 28))
            image = image[:, :, np.newaxis]
            imageList.append(image)
    return targetList, imageList

def LoadData_FMNIST(dataPath):
    targetList = []
    imageList = []
    with open(dataPath, mode='r') as dataCSV:
        lineList = list(csv.reader(dataCSV))[1:]
        for line in tqdm(lineList, desc='Loading'):
            target = int(line[0])
            targetList.append(target)
            image = np.reshape(np.array([int(pixel) for pixel in line[1:]]), (28, 28))
            image = image[:, :, np.newaxis]
            imageList.append(image)
    return targetList, imageList

def LoadData_SVHN(dataPath):
    dict = loadmat(dataPath)
    targetList = list(dict['y'].squeeze(1)-1)
    targetList = [int(target) for target in list(dict['y'].squeeze(1)-1)]
    imageList = []
    for dataIdx in range(len(targetList)):
        imageList.append(dict['X'][:, :, :, dataIdx])
    return targetList, imageList

def LoadData_CIFAR10(dataPath):
    with open(dataPath, 'rb') as data:
        dict = pickle.load(data, encoding='bytes')
        targetList = list(dict[b'labels'])
        imageList = []
        for dataIdx in tqdm(range(np.shape(dict[b'data'])[0]), desc='Loading'):
            image = np.reshape(dict[b'data'][dataIdx, :], (3, 32, 32))
            image = np.swapaxes(image, 0, 2)
            imageList.append(image)
    return targetList, imageList

class DataReader_Image(Dataset):
    def __init__(self, dataset, phase, imageSize=28, type='zadoff', flatten=True, dilate=1, bias=False):
        super(DataReader_Image, self).__init__()
        
        if dataset == 'MNIST':
            if phase == 'train':
                targetList, imageOrigList = LoadData_MNIST('./Data/MNIST/mnist_train.csv')
            else:
                targetList, imageOrigList = LoadData_MNIST('./Data/MNIST/mnist_test.csv')
        elif dataset == 'FMNIST':
            if phase == 'train':
                targetList, imageOrigList = LoadData_FMNIST('./Data/FMNIST/fashion-mnist_train.csv')
            else:
                targetList, imageOrigList = LoadData_FMNIST('./Data/FMNIST/fashion-mnist_test.csv')
        elif dataset == 'SVHN':
            if phase == 'train':
                targetList, imageOrigList = LoadData_SVHN('./Data/SVHN/train_32x32.mat')
            else:
                targetList, imageOrigList = LoadData_SVHN('./Data/SVHN/test_32x32.mat')
        elif dataset == 'CIFAR-10':
            if phase == 'train':
                fileList = ['data_batch_1', 'data_batch_2', 'data_batch_3', 'data_batch_4', 'data_batch_5']
                targetList = []
                imageOrigList = []
                for file in fileList:
                    targetNowList, imageOrigNowList = LoadData_CIFAR10('./Data/CIFAR-10/cifar-10-batches-py/'+file)
                    targetList += targetNowList
                    imageOrigList += imageOrigNowList
            else:
                targetList, imageOrigList = LoadData_CIFAR10('./Data/CIFAR-10/cifar-10-batches-py/test_batch')
        else:
            print('Warning: Dataset NOT Found!')
        channelNum = np.shape(imageOrigList[0])[-1]

        imageList = []
        for imageOrig in tqdm(imageOrigList, desc='Processing'):
            if(np.shape(imageOrig)[0]!=imageSize)or((np.shape(imageOrig)[1]!=imageSize)):
                imageNew = general.myResample(imageOrig, imageSize, imageSize)
            else:
                imageNew = imageOrig
            
            if type in ['image', 'real']:
                imageComp = (imageNew - np.mean(imageNew)) / np.mean(imageNew)
            elif type == 'comp': # NOT Maintained
                imageHalfSize = int(np.ceil(imageSize/2))
                imageComp = np.zeros((imageSize, imageHalfSize), dtype=complex)
                imageComp += (imageNew[:, 0::2] - np.mean(imageNew[:, 0::2])) / np.mean(imageNew[:, 0::2])
                imageComp[:, :imageSize-imageHalfSize] += 1j * (imageNew[:, 1::2] - np.mean(imageNew[:, 1::2])) / np.mean(imageNew[:, 1::2])
            elif type == 'zadoff':
                zadoff = general.myZadoff(imageSize*imageSize*channelNum)
                zadoffMask = np.reshape(zadoff, (imageSize, imageSize, channelNum))
                imageComp = imageNew / np.mean(imageNew) * zadoffMask
            else:
                print('Warning: Data Type NOT Supported!')
        
            if type != 'image':
                imageComp = imageComp.flatten()
                if bias:
                    imageComp = np.array(list(imageComp)+[1])
                    imageDilate = np.zeros(((imageSize*imageSize*channelNum+1)*dilate), dtype=imageComp.dtype)
                else:
                    imageDilate = np.zeros((imageSize*imageSize*channelNum*dilate), dtype=imageComp.dtype)
                imageDilate[::dilate] = imageComp
            else:
                imageDilate = np.zeros((imageSize*dilate, imageSize*dilate, channelNum), dtype=imageComp.dtype)
                imageDilate[::dilate, ::dilate, :] = imageComp
            imageList.append(imageDilate)
                
        self.targetList = targetList
        self.imageList = imageList

    def __getitem__(self, index):
        target = self.targetList[index]
        image = self.imageList[index]

        if np.iscomplex(image).any():
            imageTensor = torch.from_numpy(image).to(torch.cfloat)
        else:
            imageTensor = torch.from_numpy(image).float()
        return target, imageTensor

    def __len__(self):
        return len(self.targetList)
    
    def GetShape(self):
        classNum = 10
        return list(np.shape(self.imageList[0])), classNum
    
    def SaveData(self, fileName):
        savemat(fileName, {
            'dataList': np.array(self.imageList),
            'targetList': np.array(self.targetList)})



# Modulation Dictionary: (indexing from 0 to 23)
# 'OOK', '4ASK', '8ASK', 'BPSK', 'QPSK', '8PSK', '16PSK', '32PSK',
# '16APSK', '32APSK', '64APSK', '128APSK', '16QAM', '32QAM', '64QAM', '128QAM',
# '256QAM', 'AM-SSB-WC', 'AM-SSB-SC', 'AM-DSB-WC', 'AM-DSB-SC', 'FM', 'GMSK', 'OQPSK'
class DataReader_DeepSig(Dataset):
    def __init__(self, dataPath, waveLen=1024, span=[0, 1], type='comp', 
        moduSet=list(range(24)), snrSet=list(range(-20, 30))):
        super(DataReader_DeepSig, self).__init__()

        self.waveLen = waveLen
        self.type = type
        self.classNum = len(moduSet)

        self.waveList = []
        self.targetList = []
        for modu in moduSet:
            for snr in snrSet:
                dataName = dataPath+'data_'+str(modu+1)+'_'+str(snr)+'.mat'
                waveAll = loadmat(dataName)['wave']
                
                dataNumAll = np.shape(waveAll)[0]
                startIdx = int(span[0]*dataNumAll)
                endIdx = int(span[1]*dataNumAll)
                for dataIdx in range(startIdx, endIdx):
                    if type == 'real':
                        wave = np.stack((np.real(waveAll[dataIdx, :]), np.imag(waveAll[dataIdx, :])), axis=0)
                        self.waveList.append(wave)
                    elif type in ['comp', 'fft']:
                        self.waveList.append(waveAll[dataIdx, :])
                    else:
                        print('Warning: Data Type NOT Supported!')
                    self.targetList.append(moduSet.index(modu))
        
    def __getitem__(self, index):
        target = self.targetList[index]
        
        waveLen = self.waveLen
        wave = self.waveList[index]
        if waveLen < np.shape(wave)[0]:
            offset = np.random.randint(0, np.shape(wave)[0]-waveLen)
        else:
            offset = 0
        if np.iscomplex(wave).any():
            waveTensor = torch.from_numpy(wave[offset: offset+waveLen]).to(torch.cfloat)
        else:
            waveTensor = torch.from_numpy(wave[offset: offset+waveLen]).float()
        if self.type == 'fft':
            waveTensor = torch.fft.fft(waveTensor)
        
        return target, waveTensor

    def __len__(self):
        return len(self.targetList)
    
    def GetShape(self):
        if self.type == 'real':
            dataShape = [2, self.waveLen]
        else:
            dataShape = [self.waveLen]
        return dataShape, self.classNum
    
    def SaveData(self, fileName):
        savemat(fileName, {
            'dataList': np.array(self.waveList),
            'targetList': np.array(self.targetList)})



class DataReader_Audio(Dataset):
    def __init__(self, dataPath, waveLen=24000, ratio=6, type='fft'):
        super(DataReader_Audio, self).__init__()

        dataList = []
        targetList = []
        zadoffMask = general.myZadoff(waveLen//ratio)
        for file in tqdm(os.listdir(dataPath)):
            speechAll, _ = sf.read(dataPath+file)
            if waveLen > len(speechAll):
                continue
            for ratioIdx in [ratio//2]: # range(ratio):
                offset = int((len(speechAll)-waveLen)/2) + ratioIdx
                speech = speechAll[offset: offset+waveLen: ratio]
                if type == 'real':
                    data = speech
                elif type == 'zadoff':
                    data = speech * zadoffMask
                elif type == 'fft':
                    data = np.fft.fft(speech)
                elif 'stft' in type:
                    winLen = int(type.split('-')[-1])
                    data = np.zeros((waveLen//ratio), dtype=complex)
                    for winIdx in range(int(np.ceil(waveLen/ratio/winLen))):
                        startIdx = winIdx * winLen
                        endIdx = min((winIdx+1) * winLen, waveLen//ratio)
                        data[startIdx: endIdx] = np.fft.fft(speech[startIdx: endIdx])
                    if 'abs' in type:
                        data = np.abs(data)
                    elif 'zadoff' in type:
                        data = np.abs(data) * zadoffMask
                else:
                    print('Warning: Type NOT Found!')
                dataList.append(data)
                targetList.append(int(file[0]))
                
        self.dataList = dataList
        self.targetList = targetList

    def __getitem__(self, index):
        data = self.dataList[index]
        target = self.targetList[index]

        if np.iscomplex(data).any():
            dataTensor = torch.from_numpy(data).to(torch.cfloat)
        else:
            dataTensor = torch.from_numpy(data).float()

        return target, dataTensor

    def __len__(self):
        return len(self.targetList)

    def GetShape(self):
        classNum = 10
        return list(np.shape(self.dataList[0])), classNum

    def SaveData(self, fileName):
        savemat(fileName, {
            'dataList': np.array(self.dataList),
            'targetList': np.array(self.targetList)})