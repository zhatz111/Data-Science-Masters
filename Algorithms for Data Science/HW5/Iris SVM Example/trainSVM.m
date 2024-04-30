function model = trainSVM(X,y,options)
% This code is for educational and research purposes of comparisons.
%
% This is an example of the Support Vector Machines using the Matlab
% optimization toolbox.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Input:
%  X [dim x num_data] training vectors.
%  y [1 x num_data] labels (class) of training data (1,2,...,nclass). 
%  options.
%    ker [string] Kernel identifier
%    arg [1 x number of arguments] Kernel argument(s).
%    C SVM regularization constant
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%for linear kernel: k(a,b) = a'*b
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ker = 'linear'; 
% arg = 1;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%for polynomial kernel: k(a,b) = (a'*b+arg[2])^arg[1]
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ker = 'poly'; 
% arg = [2 1];
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%for RBF (Gaussian) kernel: k(a,b) = exp(-0.5*||a-b||^2/arg[1]^2)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ker = 'rbf'; 
% arg = 1;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%for Sigmoidal kernel: k(a,b) = tanh(arg[1]*(a'*b)+arg[2])
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ker = 'sigmoid';
% arg = [0.1 1];
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Output:
%   model.
%      X [dim x num_data] training vectors.
%      Alpha [nsv x nrule] Weights (Lagrangeans).
%      b [nrule x 1] Biases of discriminant functions.
%      svX [dim x nsv] Support vectors.
%      err [1 x 1] model classification error
%      sv_y are the labels of the support vectors 
%      sv_indx indexes of the support vectors
%      numberSV number of the support vecotrs
%     options.ker [string] Kernel identifier.
%     options.arg [1 x  narg] Kernel argument.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

ker = options.ker;
arg = options.arg;
C = options.C;

[dim,numData]=size(X);
y = y(:);
y(find(y==2)) = -1;

norm = 1;
mu = 1e-12;
eps = 1e-12;

K = kernelSVM(X,X,ker,arg);             % compute kernel matrix
H = K.*(y*y');
% Confirm that H is positive definite by checking its eigenvalues.
% eig(H)
% if any of the eigenvalues are negative add asmall numer to the diagonal
% values
H = H + mu*eye(size(H));                % add small numbers to diagonal 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The following code is used to solve the quadratic programming problems
% Matlab Optimization (works for kernels as large as 500 x 500)
% 
% 	MATLAB Optimization Toolbox (necessary)
% kernelBRodriguez.m
%
% Usages:
% [alpha,fval,exitflag] = quadprog(H,f,[],[],Aeq,beq,lb,ub,x0,opt);
% [alpha, fval, exitflag, out, lambda] =...
%                                 quadprog(H,f,[],[],Aeq,beq,lb,ub,[],opt);
%
% Inputs:
%   - H : kernel matrix with a small number added to the diagonal 
%         H = K + mu*eye(size(H)), mu = options.mu
%   - f : initial Alpha, f = -ones(n,1)
%   - Aeq : The labels of the data set, used to minimize 1/2*X'*H*X + f'*X
%   - beq : The inital bias, set to use with Aeq subject to Aeq*X = beq
%   - lb: The bounds set for: alphas >= 0, lb = zeros(n,1);
%   - ub: The bounds set for: alphas <= C, ub = C*ones(n,1);
%          lu and ub define a set of lower and upper bounds on the design
%          variables, X, so that the solution is in the range lb <= X <= ub
%   - x0: The starting point, x0 = zeros(numData,1), or use, x0=[];
%   - opt = optimset('Display','off');   % If the optimization terminates 
%                                        % before convergence it will not 
%                                        % be displayed
% 
% Outputs:
%   - alpha: The alpha values of the quadratic programming solution
%   - fval
%   - exitflag
%   - out
%   - lambda: lambda can be used as the bias
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Aeq = y';                               % Minimizes 1/2*X'*H*X + f'*X 
beq = 0;                                % subject to Aeq*X = beq
f = -ones(numData,1);                   % initial Alpha
% lu and ub define a set of lower and upper bounds on the design variables,
% X, so that the solution is in the range lb <= X <= ub
lb = zeros(numData,1);                  % 0 <= Alpha
ub = C*ones(numData,1);                 % This creates an L1-soft margin
x0 = zeros(numData,1);                  % starting point
opt = optimset('Display','off','LargeScale','off');    
                                        % If the optimization terminates 
                                        % before convergence it will not be
                                        % displayed
%[alpha,fval,exitflag] = quadprog(H,f,[],[],Aeq,beq,lb,ub,x0,opt);
alpha = quadprog(H,f,[],[],Aeq,beq,lb,ub);

sv_inx = find( alpha > eps);

% boundary (f(x)=+/-1) support vectors C > alpha > 0 
boundary_inx = find((C - eps) > alpha & alpha > eps);
if length( boundary_inx ) > 0
    b = sum(y(boundary_inx)-H(boundary_inx,sv_inx)*...
        alpha(sv_inx).*y(boundary_inx))/length( boundary_inx );
else
  b=0;
end 

prediction = K*alpha+b; 
tmp = ones(numData,1);
tmp(find(prediction<0)) = ones(length(find(prediction<0)),1).*-1;
err = (sum((abs(tmp-y)))/numData)*100;

alpha = alpha.*y;
model.alpha = alpha(sv_inx);
model.b = b;
model.options = options;
model.svX = X(:,sv_inx );
model.err = err;
model.sv_y = y(sv_inx );
model.sv_indx = sv_inx;
model.numberSV = length( sv_inx );