% This code is for educational and research purposes of comparisons. This
% is a SVM on a three class iris data set using a 1 vs all.

clear
clc
close all

irisData = readmatrix('iris.csv','Range','A2:D151');
y_1vsAll = [ones(1,50) ones(1,50).*2 ones(1,50).*2]';
y_2vsAll = [ones(1,50).*2 ones(1,50) ones(1,50).*2]';
y_3vsAll = [ones(1,50).*2 ones(1,50).*2 ones(1,50)]';

X(:,1:2) = irisData(:,3:4);
y = [ones(1,50) ones(1,50).*2 ones(1,50).*3];
%              setosa = 1, versicolor = 2, viginica = 3
%              red         green           blue

sv_indx = []; % support vectors index

options.ker = 'rbf'; % use RBF kernel
options.arg = 0.15; % kernel argument
options.C = 3; % regularization constant

model_1vsAll = trainSVM(X',y_1vsAll',options);
[yp_1vsAll,  prediction_1vsAll] = classifySVM(X', model_1vsAll);
CA_1vsAll = length(find(y_1vsAll==yp_1vsAll))/length(y_1vsAll);
sv_indx = [sv_indx; model_1vsAll.sv_indx];

model_2vsAll = trainSVM(X',y_2vsAll',options);
[yp_2vsAll,  prediction_2vsAll] = classifySVM(X', model_2vsAll);
CA_2vsAll = length(find(y_2vsAll==yp_2vsAll))/length(y_2vsAll);
sv_indx = [sv_indx; model_2vsAll.sv_indx];

model_3vsAll = trainSVM(X',y_3vsAll',options);
[yp_3vsAll,  prediction_3vsAll] = classifySVM(X', model_3vsAll);
CA_3vsAll = length(find(y_3vsAll==yp_3vsAll))/length(y_3vsAll);
sv_indx = [sv_indx; model_3vsAll.sv_indx];

tmp = [prediction_1vsAll prediction_2vsAll prediction_3vsAll]';
[value ypred] = max(tmp);
accuracy = (length(find(ypred == y))/150)*100;

[Ay,Ax] = meshgrid(linspace(-1,3,101), linspace(0,7,101));
Ax = Ax(:)';
Ay = Ay(:)';
Axy = [Ax; Ay]';

[ypred1 yt1] = classifySVM(Axy', model_1vsAll);
[ypred2 yt2] = classifySVM(Axy', model_2vsAll);
[ypred3 yt3] = classifySVM(Axy', model_3vsAll);

tmp = [yt1 yt2 yt3];
[value ypred] = max(tmp');

indx1 = find(ypred==1);
indx2 = find(ypred==2);
indx3 = find(ypred==3);

contour_1 = zeros(1,length(value));
contour_1(indx1) = value(indx1);
contour_2 = zeros(1,length(value));
contour_2(indx2) = value(indx2);
contour_3 = zeros(1,length(value));
contour_3(indx3) = value(indx3);

figure,plot(Axy(indx1,1),Axy(indx1,2),'.','Color',...
                   [249/255 219/255 219/255],'LineWidth',6,'MarkerSize',20)
hold on;plot(Axy(indx2,1),Axy(indx2,2),'.','Color',...
                   [219/255 249/255 219/255],'LineWidth',6,'MarkerSize',20)
hold on;plot(Axy(indx3,1),Axy(indx3,2),'.','Color',...
                         [204/255 204/255 1],'LineWidth',6,'MarkerSize',20)
hold on;plot(X(1:50,1),X(1:50,2),'ro','LineWidth',2,...
                                                            'MarkerSize',8)
hold on;plot(X(51:100,1),X(51:100,2),'go','LineWidth',2,...
                                                            'MarkerSize',7)
hold on;plot(X(101:150,1),X(101:150,2),'bo','LineWidth',...
                                                          2,'MarkerSize',7)
hold on;contour(reshape(Axy(:,1),101,101), reshape(Axy(:,2),101,101),...
                   reshape(ypred,101,101),'LineColor','k','LineWidth',1.5);
% For visual representation, the following can contour plats can be
% commented out
hold on;contour(reshape(Axy(:,1),101,101), reshape(Axy(:,2),101,101),...
               reshape(contour_1,101,101),'LineColor','r','LineWidth',1.5);
hold on;contour(reshape(Axy(:,1),101,101), reshape(Axy(:,2),101,101),...
               reshape(contour_2,101,101),'LineColor','g','LineWidth',1.5);
hold on;contour(reshape(Axy(:,1),101,101), reshape(Axy(:,2),101,101),...
               reshape(contour_3,101,101),'LineColor','b','LineWidth',1.5);
title('SVM Example using Matlab quadprog() and the Iris Data Set')
xlabel('Petal Length')
ylabel('Petal Width')