function [y_predict, prediction] = classifySVM(X, model)
% This code is for educational and research purposes of comparisons.
% Use the following to predict your target class.  X will be your Test data
% set.  The values alpha, b and svX are needed.  An prediction > 0 belongs
% to class 1 and an prediction < 0 belongs to class 2
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Input:
%  X [dim x num_data] test vectors.
%   model.
%      X [dim x num_data] training vectors.
%      Alpha [nsv x nrule] Weights (Lagrangeans).
%      b [nrule x 1] Biases of discriminant functions.
%      svX [dim x nsv] Support vectors.
%      err [1 x 1] model classification error

alpha = model.alpha;
b = model.b;
svX = model.svX;
ker = model.options.ker;
arg = model.options.arg;

K = kernelSVM(X, svX, ker, arg);
prediction = K*alpha+b;
[num_data,dim] = size(prediction);

y_predict = ones(num_data,1);
indx = find(prediction < 0);
y_predict(indx,1) = ones(length(indx),1).*2;
