function [r] = CalcRMSE(x_all, y_all)
    num = size(x_all, 1);
    r = NaN(1, num);
    for idx = 1: num
        x_norm = x_all(idx, :) ./ mean(x_all(idx, :));
        y_norm = y_all(idx, :) ./ mean(y_all(idx, :));
        r(idx) = sqrt(mean(abs(x_norm-y_norm).^2));
    end
end

