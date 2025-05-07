import numpy as np



def myResample(imageOrig, sizeX, sizeY):
    sizeOrigX, sizeOrigY, channelNum = np.shape(imageOrig)
    
    imageNew = np.zeros((sizeX, sizeY, channelNum))
    for idxX in range(sizeX):
        startIdxX = round(sizeOrigX/sizeX*idxX)
        endIdxX = round(sizeOrigX/sizeX*(idxX+1))
        for idxY in range(sizeY):
            startIdxY = round(sizeOrigY/sizeY*idxY)
            endIdxY = round(sizeOrigY/sizeY*(idxY+1))
            imageNew[idxX, idxY, :] = np.mean(np.mean(imageOrig[startIdxX: endIdxX, startIdxY: endIdxY], axis=0), axis=0)
    return imageNew

def myZadoff(N, R=29):
    if np.gcd(N, R) > 1:
        print('Warning: Consider Anoter Zadoff-Chu Root!')
    c = N % 2
    phaseVec = np.zeros((N)).astype(complex)
    for n in range(N):
        phaseVec[n] = np.exp(-1j*np.pi * R * n * (n+c)/N)
    return phaseVec