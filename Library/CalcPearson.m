function [r] = CalcPearson(x_all, y_all)
    num = size(x_all, 1);

    r = NaN(1, num);
    for idx = 1: num
        x = x_all(idx, :);
        y = y_all(idx, :);
        x_mean = mean(x);
        y_mean = mean(y);
        r(idx) = sum((x-x_mean).*(y-y_mean)) / sqrt(sum((x-x_mean).^2)*sum((y-y_mean).^2));
    end
end