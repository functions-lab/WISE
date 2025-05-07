function [seq] = myZadoff(N)
    R = 29;
    if gcd(N, R) > 1
        disp("Warning: Consider Another Zadoff-Chu Root!");
    end
    c = mod(N, 2);
    seq = zeros(1, N);
    for n = 0: N-1
        % wikipedia
        seq(n+1) = exp(-1i*pi*R*n*(n+c)/N);
    end
end