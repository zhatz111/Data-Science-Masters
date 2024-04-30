function K = kernelSVM(X1, X2, ker, arg)
% This code is for educational and research purposes of comparisons.
%
% kernelSVM.m this function valuates kernel function and returns
% kernel matrix K
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Input:
%  X1 [dim x numberOfData1] input matrices.
%  X2 [dim x numberOfData2] input matrices.
%  In most cases X1 and X2 are the same.
%  ker [string] Kernel identifier.
%  arg [1 x (number of arguments)] Kernel argument(s).
%
% Output:
%  K values of the kernel
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%for gaussian kernel: k(X1,X2) = 
%    (1/(sqrt(2*pi)*arg(1)))*exp(-0.5*(((X1-X2)'*(X1-X2))/(arg(1)*arg(1))))
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ker = 'gaussian'; 
% arg = 0.1;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%for linear kernel: k(X1,X2) = X1'*X2
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ker = 'linear'; 
% arg = 1;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%for polynomial kernel: k(X1,X2) = (X1'*X2+arg(2))^arg(1)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ker = 'poly'; 
% arg = [2 1];
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%for RBF kernel: k(X1,X2) = exp(-0.5*||X1-X2||^2/arg[1]^2)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ker = 'rbf'; 
% arg = 1;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%for Sigmoidal kernel: k(X1,X2) = tanh(arg[1]*(X1'*X2)+arg[2])
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ker = 'sigmoid';
% arg = [0.1 1];
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

[dim1,numData1]=size(X1);
[dim2,numData2]=size(X2);
if strcmp(ker,'Fourier')
    arg = dim1;
elseif strcmp(ker,'RBFFourier')
    arg = dim1;
end
K = zeros(numData1,numData2);
for i = 1:numData1
    for j = 1:numData2
        K(i,j) = kernel(X1(:,i),X2(:,j),ker,arg);
    end
end

function k = kernel(X1,X2,ker,arg)

switch ker
    % linear kernel -- k(X1,X2) = X1'*X2
    case 'linear'
        k = X1'*X2;
    % polynomial kernel -- poly degree arg[1], k(X1,X2) = (X1'*X2+arg[2])^arg[1]
    case 'poly'
        k = (X1'*X2 + arg(2))^arg(1);
    % radial basis kernel -- arg[1] = sigma, k(X1,X2) = exp(-0.5*||X1-X2||^2/arg[1]^2)
    case 'rbf'
        k = exp(-0.5*(((X1-X2)'*(X1-X2))/(arg(1)*arg(1))));
    % Gaussian kernel -- sigma, k(X1,X2)=1/(2*pi^(N/2)*sqrt(sigma^2)) exp(..)
    case 'Gaussian'
        %k = (1/(sqrt(2*pi)*arg(1)))*exp(-0.5*(((X1-X2)'*(X1-X2))/(arg(1)*arg(1))));
        k = (1/(arg(1)*(2*pi)^(dim1/2)))*exp(-0.5*(((X1-X2)'*(X1-X2))/(arg(1)*arg(1))));
    % sigmoid kernel -- k(X1,X2) = tanh(arg[1]*(X1'*X2)+arg[2])
    case 'sigmoid'     
        k = tanh( arg(1)*(X1'*X2) + arg(2));
    % Fourier kernel -- k(X1,X2) = sum(abs(fft(X1)-fft(X2)))/arg;
    case 'Fourier'
        %k = sum(abs(fft(X1)-fft(X2)))/dim1;
        k = ((abs(fft(X1)-fft(X2)))'*(abs(fft(X1)-fft(X2))))/arg;
   % RBF combined with Fourier kernel -- 
   %                  x = ((abs(fft(X1)-fft(X2)))'*(abs(fft(X1)-fft(X2))));
   %                  k = exp(-0.5*((x)/(arg(1)*arg(1))));
    case 'RBFFourier'
        x = ((abs(fft(X1)-fft(X2)))'*(abs(fft(X1)-fft(X2))));
        k = exp(-0.5*((x)/(arg(1)*arg(1))));
    otherwise
        k = 0;
end