% This code is for educational and research purposes of comparisons. This
% is a Parzen three class example using the iris data set. This code has
% been designed for Summer 2022 HW 3 Problem 4. 

clear;
clc;
close all;

iris_data.X = readmatrix('hw3_iris.csv','Range','A2:D151');
iris_data.Y = [ones(1,50) ones(1,50).*2 ones(1,50).*3];
%              setosa = 1, versicolor = 2, virginica = 3
%              red         green           blue

model =  hw3_fishersMultiClassFeatureRanking(iris_data,1);% Rank features
numFeatures = model.featureIndex(1:2);%Select the top two ranked features
X = iris_data.X(:,numFeatures); % use the top two features petal length 
                                % and petal width 
%X = iris_data.X'; % use all of the features
Y = iris_data.Y';

spread = 0.1; % this is the h value in the equation

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Simple Classification Example
% Parzen Window
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
p1 = [];
p2 = [];
p3 = [];
p1 = zeros(1,size(X,1)); 
p2 = zeros(1,size(X,1));
p3 = zeros(1,size(X,1));
for i=1:150
    p1(i) = (1/50)*sum(hw3_gaussianKernel(X(i,:), X(1:50,:), spread));
    p2(i) = (1/50)*sum(hw3_gaussianKernel(X(i,:), X(51:100,:), spread));
    p3(i) = (1/50)*sum(hw3_gaussianKernel(X(i,:), X(101:150,:), spread));
end

ytmp = [p1; p2; p3];

[value ypred]= max(ytmp);
inx1 = find(Y==1);
inx2 = find(Y==2);
inx3 = find(Y==3);
CA = length(find(Y==ypred'))/length(Y); % This gives use the classification
                                       % accuracy.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Problem 4 (a)
% Using 5-fold cross-validation
% Parzen Window
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
cross_Val = 5;

[indx_trn,indx_tst] = hw3_crossval(length(X),cross_Val);

test = [];
ytest = [];
train = [];
yTrain = [];

for k = 1:cross_Val
    
    test = X(indx_tst{k},:);
    yTest = Y(indx_tst{k});
    train = X(indx_trn{k},:);
    yTrain = Y(indx_trn{k});
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Class 1 - Setosa
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    train1 = [];
    cnt = 1;
    for iTrn = 1:length(yTrain)
        if yTrain(iTrn) == 1
            train1(cnt,:) = train(iTrn,:); 
            cnt = cnt + 1;
        end 
    end
    p1 = [];
    p1 = zeros(length(test),1);
    for i=1:length(test)
        p1(i) = 1/length(train1)*sum(hw3_gaussianKernel(test(i,:), train1, spread));
    end
        
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Class 2 - Versicolor
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
    train2 = [];
    cnt = 1;
    for iTrn = 1:length(yTrain)
        if yTrain(iTrn) == 2
            train2(cnt,:) = train(iTrn,:); 
            cnt = cnt + 1;
        end 
    end
    p2 = [];
    p2 = zeros(length(test),1);
    for i=1:length(test)
        p2(i) = 1/length(train2)*sum(hw3_gaussianKernel(test(i,:), train2, spread));
    end
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Class 3 - Virginica
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
    train3 = [];
    cnt = 1;
    for iTrn = 1:length(yTrain)
        if yTrain(iTrn) == 3
            train3(cnt,:) = train(iTrn,:); 
            cnt = cnt + 1;
        end 
    end
    p3 = [];
    p3 = zeros(length(test),1);
    for i=1:length(test)
        p3(i) = 1/length(train3)*sum(hw3_gaussianKernel(test(i,:), train3, spread));
    end
    
    ytmp = [p1 p2 p3]';
    [value ypred]= max(ytmp);

    accuracy(k) = (length(find(ypred' == yTest))/length(yTest))*100;

    [a1p1, a2p1, a3p1, a1p2, a2p2, a3p2, a1p3, a2p3, a3p3] = ...
                                    hw3_confusion_matrix_3Class(ypred', yTest);
                                 
    a1p1(k) = a1p1;
    a2p1(k) = a2p1;
    a3p1(k) = a3p1;
    a1p2(k) = a1p2;
    a2p2(k) = a2p2;
    a3p2(k) = a3p2;
    a1p3(k) = a1p3;
    a2p3(k) = a2p3;
    a3p3(k) = a3p3;          
    
    fprintf('\n-------------------------------------------------------\n')
    fprintf('                Confusion Matrix for Fold-%d\n',k)
    fprintf('-------------------------------------------------------\n')
    fprintf('                           Actual                      \n')
    fprintf('P|-----------------------------------------------------\n')
    fprintf('r|             Setosa   Versicolor   Virginica          \n')
    fprintf('e|                                                     \n')
    fprintf('d| Setosa       %3.0f       %3.0f         %3.0f\n',...
                                                 a1p1(k), a2p1(k), a3p1(k))
    fprintf('i| Versicolor   %3.0f       %3.0f         %3.0f\n',...
                                                 a1p2(k), a2p2(k), a3p2(k))
    fprintf('c| Virginica    %3.0f       %3.0f         %3.0f\n',...
                                                 a1p3(k), a2p3(k), a3p3(k))
    fprintf('t| \n');
    fprintf('e| \n');
    fprintf('d| \n');
    fprintf('--------------------------------------------------------\n\n')
    
end

fprintf ('\nThe Overall Classification Accuracy is: %3.1f%% +/- %2.1f%%\n',...
                                             mean(accuracy), std(accuracy))   

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Problem 4 (b) i
% Simple 1-D Example
% Parzen Window
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
ax = 0:0.05:8; % used to test the space from 0 to 8 in increments of 0.05

p1 = [];
p2 = [];
p3 = [];
p1 = zeros(length(ax),1); 
p2 = zeros(length(ax),1);
p3 = zeros(length(ax),1);  
for i=1:length(ax)
    p1(i) = (1/50)*sum(hw3_gaussianKernel(ax(i), X(1:50,2), spread));
    p2(i) = (1/50)*sum(hw3_gaussianKernel(ax(i), X(51:100,2), spread));
    p3(i) = (1/50)*sum(hw3_gaussianKernel(ax(i), X(101:150,2), spread));
end

figure,plot(ax',p1,'r','MarkerSize',8,'LineWidth',1)
hold on,plot(ax',p2,'g','LineWidth',1)
hold on,plot(ax',p3,'b','LineWidth',1)                                       
        
hold on;plot(X(1:50,2),zeros(1,50),'ro','MarkerSize',8,'LineWidth',1.5)
hold on;plot(mean(X(1:50,2)),0,'rx','MarkerSize',10,'LineWidth',2)
hold on;plot(X(51:100,2),zeros(1,50),'g*','MarkerSize',8,'LineWidth',1.5)
hold on;plot(mean(X(51:100,2)),0,'gx','MarkerSize',10,'LineWidth',2)
hold on;plot(X(101:150,2),zeros(1,50),'bo','MarkerSize',8,'LineWidth',1.5)
hold on;plot(mean(X(101:150,2)),0,'bx','MarkerSize',10,'LineWidth',2)                                         
                                         
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Problem 4 (b) ii
% Simple 2-D Example
% Parzen Window
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The following ax and ay variables test the kernel with the Iris data to
% determine the boundaries for the classes
ax=-1:0.04:3;
ay=0:0.07:7;
[Ax,Ay] = meshgrid(linspace(-1,3,101), linspace(0,7,101));
Axy = [Ax(:) Ay(:)];
lngtAxy = length(Axy);

p1 = [];
p2 = [];
p3 = [];
p1=zeros(lngtAxy,1); 
p2=zeros(lngtAxy,1); 
p3=zeros(lngtAxy,1);
for i=1:lngtAxy
    p1(i) = (1/50)*sum(hw3_gaussianKernel(Axy(i,:), X(1:50,:), spread));
    p2(i) = (1/50)*sum(hw3_gaussianKernel(Axy(i,:), X(51:100,:), spread));
    p3(i) = (1/50)*sum(hw3_gaussianKernel(Axy(i,:), X(101:150,:), spread));
end

ytmp = [p1 p2 p3]';
[value ypred]= max(ytmp);
indx1 = find(ypred==1);
indx2 = find(ypred==2);
indx3 = find(ypred==3);
figure,plot(Ax(indx1),Ay(indx1),'.','Color',[249/255 219/255 219/255],'LineWidth',6,'MarkerSize',20)
hold on;plot(Ax(indx2),Ay(indx2),'.','Color',[219/255 249/255 219/255],'LineWidth',6,'MarkerSize',20)
hold on;plot(Ax(indx3),Ay(indx3),'.','Color',[204/255 204/255 1],'LineWidth',6,'MarkerSize',20)
hold on;plot(X(inx1,1),X(inx1,2),'ro','LineWidth',2,'MarkerSize',8)
hold on;plot(X(inx2,1),X(inx2,2),'g*','LineWidth',2,'MarkerSize',7)
hold on;plot(X(inx3,1),X(inx3,2),'bo','LineWidth',2,'MarkerSize',7)
hold on;contour(reshape(Ax,101,101), reshape(Ay,101,101),reshape(ypred,101,101),'LineColor','k','LineWidth',1.5);
hold on;contour(reshape(Ax,101,101), reshape(Ay,101,101),reshape(p1,101,101),'LineColor','r','LineWidth',1.5);
hold on;contour(reshape(Ax,101,101), reshape(Ay,101,101), reshape(p2,101,101),'LineColor','g','LineWidth',1.5);
hold on;contour(reshape(Ax,101,101), reshape(Ay,101,101), reshape(p3,101,101),'LineColor','b','LineWidth',1.5);
title('Parzen Windowing with Gaussian Kernel')
xlabel('Petal Width')
ylabel('Petal Length')
axis([0 3 0.5 7])