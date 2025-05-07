import numpy as np
import matplotlib.pyplot as plt
from scipy.io import savemat
import torch

def SaveModel(path, token, Model, resultIn, isMat=False, isModel=False):
    if isMat:
        fig, ax = plt.subplots()
        # ax.imshow(np.mean(resultIn['matTest'][-1], axis=0))
        ax.imshow(resultIn['matTest'][-1])
        fig.savefig(path + 'mat_'+token+'.png')
        plt.close(fig)
    
    if isModel:
        torch.save(Model.state_dict(), path+'model_'+token+'.pth')

    resultOut = {}
    resultOut.update(resultIn)
    weightList = Model.state_dict()
    weightDict = {}
    layerIdx = 0
    for layer in weightList:
        layerIdx += 1
        weightDict['Matrix_'+str(layerIdx)] = weightList[layer].detach().cpu().numpy()
    resultOut.update(weightDict)
    savemat(path+'model_'+token+'.mat', resultOut)
    
    return resultOut