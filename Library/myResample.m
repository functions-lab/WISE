function [imageNew] = myResample(imageOrig, sizeX, sizeY)
    [sizeOrigX, sizeOrigY] = size(imageOrig);

    imageNew = zeros(sizeX, sizeY);
    for idxX = 1: sizeX
        startIdxX = round(sizeOrigX/sizeX*(idxX-1))+1;
        endIdxX = round(sizeOrigX/sizeX*idxX);
        for idxY = 1: sizeY
            startIdxY = round(sizeOrigY/sizeY*(idxY-1))+1;
            endIdxY = round(sizeOrigY/sizeY*idxY);
            imageNew(idxX, idxY) = mean(imageOrig(startIdxX: endIdxX, startIdxY: endIdxY), 'all');
        end
    end
end

