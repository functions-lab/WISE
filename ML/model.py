import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import general



# def convolution(input_1, input_2):
#     inputSize_1 = input_1.size()[-1]
#     inputSize_2 = input_2.size()[-1]
#     outputSize = inputSize_1 + inputSize_2 - 1
#     outputList = []
#     for index in range(outputSize):
#         inputIdx_1 = torch.arange(max([0, index-inputSize_2+1]), min([index+1, inputSize_1]))
#         if input_1.get_device() >= 0:
#             inputIdx_1 = inputIdx_1.to(input_1.get_device())
#         inputNow_1 = torch.index_select(input_1, -1, inputIdx_1)
#         inputIdx_2 = torch.flip(torch.arange(max([0, index-inputSize_1+1]), min([index+1, inputSize_2])), dims=(0,))
#         if input_2.get_device() >= 0:
#             inputIdx_2 = inputIdx_2.to(input_2.get_device())
#         inputNow_2 = torch.index_select(input_2, -1, inputIdx_2)
#         outputNow = torch.sum(inputNow_1*inputNow_2, dim=-1)
#         outputList.append(outputNow)
#     output = torch.stack(outputList, dim=-1)
#     return output

def convolution_new(input_1, input_2, expand=False):
    batchNum = input_1.size()[0]
    inputSize_1 = input_1.size()[-1]
    inputSize_2 = input_2.size()[-1]
    outputSize = inputSize_1 + inputSize_2 - 1
    
    input_2_reverse = torch.flip(input_2, dims=(-1, ))
    
    output = torch.zeros((batchNum, outputSize)).to(input_1)
    for index in range(outputSize):
        inputNow_1 = input_1[:, max([0, index-inputSize_2+1]): min([index+1, inputSize_1])]
        if expand:
            inputNow_2 = input_2_reverse[max([0, inputSize_2-index-1]): min([outputSize-index, inputSize_2])]
        else:
            inputNow_2 = input_2_reverse[:, max([0, inputSize_2-index-1]): min([outputSize-index, inputSize_2])]
        output[:, index] = torch.sum(inputNow_1*inputNow_2, dim=-1)
    
    return output

class ConvSelfLayer_new(nn.Module):
    def __init__(self):
        super(ConvSelfLayer_new, self).__init__()
    
    def forward(self, x_0):
        x_1 = convolution_new(x_0, x_0, expand=False)
        return x_1

def convolution_std(input):
    batchNum, _, inputSize = input.size()
    outputSize = inputSize * 2 - 1
    
    output = torch.zeros((batchNum, outputSize)).to(input)
    for batchIdx in range(batchNum):
        inputNow = input[batchIdx, :, :].unsqueeze(0)
        output[batchIdx, :] = F.conv1d(inputNow, torch.flip(inputNow, dims=(-1,)), padding=inputSize-1)
    
    return output.unsqueeze(1)

class ConvSelfLayer_std(nn.Module):
    def __init__(self):
        super(ConvSelfLayer_std, self).__init__()
    
    def forward(self, x_0):
        x_1 = convolution_std(x_0)
        return x_1

class ZadoffLayer(nn.Module):
    def __init__(self, featNum, R=29):
        super(ZadoffLayer, self).__init__()
        
        self.phaseShift = general.myZadoff(featNum, R=R)
    
    def forward(self, x_0):
        phaseShift = torch.from_numpy(self.phaseShift).to(x_0)
        batchNum = x_0.size()[0]
        channelNum = x_0.size()[1]
        x_1 = torch.abs(x_0)
        x_2 = x_1 * phaseShift.unsqueeze(0).unsqueeze(0).repeat(batchNum, channelNum, 1)
        return x_2

class AbsLayer(nn.Module):
    def __init__(self):
        super(AbsLayer, self).__init__()
    
    def forward(self, x_0):
        x_1 = torch.abs(x_0).to(x_0)
        return x_1
    
class ReLULayer(nn.Module):
    def __init__(self):
        super(ReLULayer, self).__init__()
    
    def forward(self, x_0):
        x_1 = torch.complex(F.relu(torch.real(x_0)), F.relu(torch.imag(x_0)))
        return x_1



class ANN_Real(nn.Module):
    def __init__(self, dataShape, classNum, hiddenList=[100]):
        super(ANN_Real, self).__init__()

        featOut = 1
        for size in dataShape:
            featOut *= size

        LineList = []
        for hidden in hiddenList:
            featIn = featOut
            featOut = hidden
            Line = nn.Sequential(
                nn.Linear(in_features=featIn, out_features=featOut, bias=False),
                # nn.BatchNorm1d(num_features=featOut),
                # nn.ReLU(inplace=True),
                nn.Dropout(p=0.5)
            )
            LineList.append(Line)
        self.LineList = nn.ModuleList(LineList)
            
        self.LineLast = nn.Sequential(
            nn.Linear(in_features=featOut, out_features=classNum, bias=False))
    
    def forward(self, x_0):
        x_1_out = x_0
        for Line in self.LineList:
            x_1_in = x_1_out
            x_1_out = Line(x_1_in)
            x_1_out = torch.abs(x_1_out)
        x_1 = x_1_out

        x_2 = self.LineLast(x_1)
        x_2 = torch.abs(x_2)
        
        return x_2



class ANN_Comp(nn.Module):
    def __init__(self, dataShape, classNum, hiddenList=[100], act='conv'):
        super(ANN_Comp, self).__init__()

        featOut = 1
        for size in dataShape:
            featOut *= size

        self.FCList = []
        for hiddenIdx in range(len(hiddenList)):
            hidden = hiddenList[hiddenIdx]

            featIn = featOut
            featOut = hidden
            weightInit = torch.randn((featIn, featOut), dtype=torch.cfloat, requires_grad=True) / featIn
            exec('self.weight_'+str(hiddenIdx)+' = nn.Parameter(weightInit)')
            if act == 'zadoff':
                activation = ZadoffLayer(featNum=hidden)
            elif act == 'conv':
                activation = ConvSelfLayer_new()
                featOut = featOut * 2 - 1
            else:
                print('Warning: Activation Function NOT Found!')
            exec('self.FCList.append((self.weight_'+str(hiddenIdx)+', activation))')

        self.weightLast = nn.Parameter(
            torch.randn((featOut, classNum), dtype=torch.cfloat, requires_grad=True))
    
    def forward(self, x_0):
        x_1_out = x_0
        for (weight, activation) in self.FCList:
            x_1_in = x_1_out
            x_1_out = torch.matmul(x_1_in, weight)
            x_1_out = activation(x_1_out)
        x_1 = x_1_out

        x_2 = torch.matmul(x_1, self.weightLast)
        x_2 = torch.abs(x_2)
        
        return x_2



class CNN_Comp(nn.Module):
    def __init__(self, dataShape, classNum, kernelList=[100], act='conv'):
        super(CNN_Comp, self).__init__()

        self.classNum = classNum
        
        featOut = 1
        for size in dataShape:
            featOut *= size

        self.ConvList = []
        for kernelIdx in range(len(kernelList)-1):
            kernel = kernelList[kernelIdx]

            weightInit = torch.randn((kernel), dtype=torch.cfloat, requires_grad=True) / kernel
            featOut += kernel - 1
            exec('self.weight_'+str(kernelIdx)+' = nn.Parameter(weightInit)')
            if act == 'zadoff':
                activation = ZadoffLayer(featOut)
            elif act == 'conv':
                activation = ConvSelfLayer_new()
                featOut = featOut * 2 - 1
            else:
                print('Warning: Activation Function NOT Found!')
            exec('self.ConvList.append((self.weight_'+str(kernelIdx)+', activation))')

        kernel = kernelList[-1]
        self.weightLast = nn.Parameter(
            torch.randn((kernel), dtype=torch.cfloat, requires_grad=True)/kernel)
        featOut += kernel - 1
        
        if (featOut-classNum) % 2 == 1:
            self.offset = (featOut-classNum-1)//2
        else:
            self.offset = (featOut-classNum)//2
    
    def forward(self, x_0):
        x_1_out = x_0
        for (weight, activation) in self.ConvList:
            x_1_in = x_1_out
            x_1_out = convolution_new(x_1_in, weight, expand=True)
            x_1_out = activation(x_1_out)
        x_1 = x_1_out

        x_2 = convolution_new(x_1, self.weightLast, expand=True)
        x_2 = x_2[:, self.offset: self.offset+self.classNum]
        x_2 = torch.abs(x_2)
        
        return x_2



class CNN_Std(nn.Module):
    def __init__(self, dataShape, classNum, kernelList=[100], act='conv'):
        super(CNN_Std, self).__init__()

        self.classNum = classNum
        
        featOut = 1
        for size in dataShape:
            featOut *= size

        ConvList = []
        for kernelIdx in range(len(kernelList)-1):
            kernel = kernelList[kernelIdx]

            featOut += kernel - 1
            if act == 'zadoff':
                Conv = nn.Sequential(
                    nn.Conv1d(in_channels=1, out_channels=1, kernel_size=kernel, padding=kernel-1, bias=False, dtype=torch.complex64),
                    ZadoffLayer(featNum=featOut))
            elif act == 'conv':
                Conv = nn.Sequential(
                    nn.Conv1d(in_channels=1, out_channels=1, kernel_size=kernel, padding=kernel-1, bias=False, dtype=torch.complex64),
                    ConvSelfLayer_std())
                featOut = featOut * 2 - 1
            else:
                print('Warning: Activation Function NOT Found!')
            ConvList.append(Conv)
        self.ConvList = nn.ModuleList(ConvList)

        kernel = kernelList[-1]
        self.ConvLast = nn.Conv1d(in_channels=1, out_channels=1, kernel_size=kernel, padding=kernel-1, bias=False, dtype=torch.complex64)
        featOut += kernel - 1
        
        if (featOut-classNum) % 2 == 1:
            self.offset = (featOut-classNum-1)//2
        else:
            self.offset = (featOut-classNum)//2
    
    def forward(self, x_0):
        x_1_out = x_0.unsqueeze(1)
        for Conv in self.ConvList:
            x_1_in = x_1_out
            x_1_out = Conv(x_1_in)
        x_1 = x_1_out

        x_2 = self.ConvLast(x_1)
        x_2 = x_2.squeeze(1)
        x_2 = x_2[:, self.offset: self.offset+self.classNum]
        x_2 = torch.abs(x_2)
        
        return x_2



class Hybrid_Image(nn.Module):
    def __init__(self, dataShape, classNum, 
        bias=True, kernelList=[3, 3, 3, 3, 3, 3, 3], channelList=[64, 64, 64, 64, 64, 64, 64], hiddenList=[128, 128]):
        super(Hybrid_Image, self).__init__()

        self.classNum = classNum
        
        channelOut = dataShape[-1]
        ConvList = []
        for kernelIdx in range(len(kernelList)):
            kernel = kernelList[kernelIdx]
            channel = channelList[kernelIdx] if kernelIdx<len(channelList) else 64
            
            channelIn = channelOut
            channelOut = channel
            Conv = nn.Sequential(
                nn.Conv2d(
                    in_channels=channelIn, out_channels=channelOut, 
                    kernel_size=kernel, padding=(kernel-1)//2, bias=bias),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2))

            ConvList.append(Conv)
        self.ConvList = nn.ModuleList(ConvList)
        
        featOut = dataShape[0] * dataShape[1] * channelOut // (4**len(channelList))
        FCList = []
        for hidden in hiddenList:
            featIn = featOut
            featOut = hidden
            FC = nn.Sequential(
                nn.Linear(in_features=featIn, out_features=featOut, bias=bias),
                nn.ReLU(inplace=True))

            FCList.append(FC)
        self.FCList = nn.ModuleList(FCList)
        
        self.FCLast = nn.Sequential(
            nn.Linear(in_features=featOut, out_features=classNum, bias=bias),
            nn.Softmax(dim=-1))
            
    def forward(self, x_0):
        # x_1_out = torch.stack((torch.real(x_0), torch.imag(x_0)), dim=1)
        x_1_out = torch.transpose(x_0, 1, -1)
        for Conv in self.ConvList:
            x_1_in = x_1_out
            x_1_out = Conv(x_1_in)
        x_1 = x_1_out.squeeze(1)
        
        x_2_out = torch.flatten(x_1, start_dim=1, end_dim=-1)
        for FC in self.FCList:
            x_2_in = x_2_out
            x_2_out = FC(x_2_in)
        x_2 = x_2_out
        
        x_3 = self.FCLast(x_2)

        return x_3



class Hybrid_Std(nn.Module):
    def __init__(self, dataShape, classNum, 
        bias=True, kernelList=[3, 3, 3, 3, 3, 3, 3], channelList=[64, 64, 64, 64, 64, 64, 64], hiddenList=[128, 128]):
        super(Hybrid_Std, self).__init__()

        self.classNum = classNum
        
        channelOut = dataShape[-1]
        ConvList = []
        for kernelIdx in range(len(kernelList)):
            kernel = kernelList[kernelIdx]
            channel = channelList[kernelIdx] if kernelIdx<len(channelList) else 64
            
            channelIn = channelOut
            channelOut = channel
            Conv = nn.Sequential(
                nn.Conv1d(
                    in_channels=channelIn, out_channels=channelOut, 
                    kernel_size=kernel, padding=(kernel-1)//2, bias=bias),
                nn.ReLU(inplace=True),
                nn.MaxPool1d(kernel_size=2))

            ConvList.append(Conv)
        self.ConvList = nn.ModuleList(ConvList)
        
        featOut = np.prod(np.array(dataShape)[:-1]) * channelOut // (2**len(channelList))
        FCList = []
        for hidden in hiddenList:
            featIn = featOut
            featOut = hidden
            FC = nn.Sequential(
                nn.Linear(in_features=featIn, out_features=featOut, bias=bias),
                # nn.Dropout(p=0.5),
                nn.ReLU(inplace=True))

            FCList.append(FC)
        self.FCList = nn.ModuleList(FCList)
        
        self.FCLast = nn.Sequential(
            nn.Linear(in_features=featOut, out_features=classNum, bias=bias),
            # nn.Dropout(p=0.5),
            nn.Softmax(dim=-1))

    def forward(self, x_0):
        # x_1_out = torch.stack((torch.real(x_0), torch.imag(x_0)), dim=1)
        x_1_out = torch.flatten(x_0, start_dim=1, end_dim=-1).unsqueeze(1)
        x_1_out = x_0.unsqueeze(1)
        for Conv in self.ConvList:
            x_1_in = x_1_out
            x_1_out = Conv(x_1_in)
        x_1 = x_1_out.squeeze(1)
        
        x_2_out = torch.flatten(x_1, start_dim=1, end_dim=-1)
        for FC in self.FCList:
            x_2_in = x_2_out
            x_2_out = FC(x_2_in)
        x_2 = x_2_out
        
        x_3 = self.FCLast(x_2)

        return x_3



class Hybrid(nn.Module):
    def __init__(self, dataShape, classNum, 
        bias=False, kernelList=[200], channelList=[1], window=-1, hiddenList=[], act='conv'):
        super(Hybrid, self).__init__()

        self.classNum = classNum
        self.window = window
        
        featOut = 1
        for size in dataShape:
            featOut *= size

        ConvList = []
        for kernelIdx in range(len(kernelList)):
            kernel = kernelList[kernelIdx]
            channel = channelList[kernelIdx] if kernelIdx<len(channelList) else 1

            featOut += kernel - 1
            if act == 'relu':
                Conv = nn.Sequential(
                    nn.Conv1d(in_channels=1, out_channels=channel, 
                        kernel_size=kernel, padding=kernel-1, bias=bias, dtype=torch.complex64),
                    ReLULayer())
            elif act == 'abs':
                Conv = nn.Sequential(
                    nn.Conv1d(in_channels=1, out_channels=channel, 
                        kernel_size=kernel, padding=kernel-1, bias=bias, dtype=torch.complex64),
                    AbsLayer())
            elif act == 'zadoff':
                Conv = nn.Sequential(
                    nn.Conv1d(in_channels=1, out_channels=channel, 
                        kernel_size=kernel, padding=kernel-1, bias=bias, dtype=torch.complex64),
                    ZadoffLayer(featNum=featOut))
            elif act == 'conv':
                Conv = nn.Sequential(
                    nn.Conv1d(in_channels=1, out_channels=channel, 
                        kernel_size=kernel, padding=kernel-1, bias=bias, dtype=torch.complex64),
                    ConvSelfLayer_std())
                featOut = featOut * 2 - 1
            else:
                print('Warning: Activation Function NOT Found!')
            ConvList.append(Conv)
        self.ConvList = nn.ModuleList(ConvList)
        
        if window != -1:
            if (featOut-window) % 2 == 1:
                self.offset = (featOut-window-1)//2
            else:
                self.offset = (featOut-window)//2
            featOut = window
        else:
            self.offset = 0
        
        self.FCList = []
        for hiddenIdx in range(len(hiddenList)):
            hidden = hiddenList[hiddenIdx]

            featIn = featOut
            featOut = hidden
            weightInit = torch.randn((featIn, featOut), dtype=torch.cfloat, requires_grad=True) / featIn
            exec('self.weight_'+str(hiddenIdx)+' = nn.Parameter(weightInit)')
            if act == 'relu':
                activation = ReLULayer()
            elif act == 'abs':
                activation = AbsLayer()
            elif act == 'zadoff':
                activation = ZadoffLayer(featNum=hidden)
            elif act == 'conv':
                activation = ConvSelfLayer_std()
                featOut = featOut * 2 - 1
            else:
                print('Warning: Activation Function NOT Found!')
            exec('self.FCList.append((self.weight_'+str(hiddenIdx)+', activation))')
        
        self.weightLast = nn.Parameter(
            torch.randn((featOut, classNum), dtype=torch.cfloat, requires_grad=True))
    
    def forward(self, x_0):
        x_2_out = x_0.unsqueeze(1)
        for Conv in self.ConvList:
            x_2_in = x_2_out
            x_2_out = Conv(x_2_in)
            x_2_out = torch.mean(x_2_out, dim=1, keepdim=True)
        x_2 = x_2_out.squeeze(1)
        
        if self.window != -1:
            x_3_out = x_2[:, self.offset: self.offset+self.window]
        else:
            x_3_out = x_2
        
        for (weight, activation) in self.FCList:
            x_3_in = x_3_out
            x_3_out = torch.matmul(x_3_in, weight)
            x_3_out = activation(x_3_out.unsqueeze(1)).squeeze(1)
        x_3 = x_3_out

        x_4 = torch.matmul(x_3, self.weightLast)
        x_4 = torch.abs(x_4)
        
        return x_4
