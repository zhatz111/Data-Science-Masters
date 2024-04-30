% This code is for educational and research purposes of comparisons. This
% is a Matlab SVM three class example using the iris data set.

clear;
clc;
close all;

weka_data = arffparser('read', 'iris.arff'); % load data provided by WEKA
iris_data.X(:,1) = weka_data.sepallength.values';
iris_data.X(:,2) = weka_data.sepalwidth.values';
iris_data.X(:,3) = weka_data.petallength.values'; % Petal Length
iris_data.X(:,4) = weka_data.petalwidth.values';  % Petal Width
iris_data.Y = [ones(1,50) ones(1,50).*2 ones(1,50).*3]';
%              setosa = 1, versicolor = 2, virginica = 3
%              red         green           blue

SVMModels = cell(3,1);
classes = unique(iris_data.Y);
rng(1); % For reproducibility

for j = 1:numel(classes)
    indx = ismember(iris_data.Y,classes(j)); % Identifies the indicies for each classifier
    SVMModels{j} = fitcsvm(iris_data.X(:,[4 3]),indx,'ClassNames',[false true],'Standardize',true,...
        'KernelFunction','gaussian','BoxConstraint',1);
end

for j = 1:numel(classes)
    [~,score] = predict(SVMModels{j},iris_data.X(:,[4 3]));
    Scores(:,j) = score(:,2); % Second column contains positive-class scores
end
[~,ypred] = max(Scores,[],2);
CA = length(find(iris_data.Y==ypred))/length(iris_data.Y); % This gives use the classification
                                       % accuracy.
inx1 = find(ypred==1);
inx2 = find(ypred==2);
inx3 = find(ypred==3);

% The following ax and ay variables test the kernel with the Iris data to
% determine the boundaries for the classes
ax=-1:0.04:3;
ay=0:0.07:7;
[Ax,Ay] = meshgrid(linspace(-1,3,101), linspace(0,7,101));
Ax = Ax(:)';
Ay = Ay(:)';

N = size([Ax; Ay]',1);
Scores = zeros(N,numel(classes));
for j = 1:numel(classes)
    [~,score] = predict(SVMModels{j},[Ax; Ay]');
    Scores(:,j) = score(:,2); % Second column contains positive-class scores
end
[~,ypred] = max(Scores,[],2);
scores1 = zeros(length(Scores(:,1)),1);
posIndx = find(Scores(:,1)>0);
scores1(posIndx) = Scores(posIndx,1);
scores2 = zeros(length(Scores(:,2)),1);
posIndx = find(Scores(:,2)>0);
scores2(posIndx) = Scores(posIndx,2);
scores3 = zeros(length(Scores(:,3)),1);
posIndx = find(Scores(:,3)>0);
scores3(posIndx) = Scores(posIndx,3);

X = iris_data.X(:,[4 3])';

indx1 = find(ypred==1);
indx2 = find(ypred==2);
indx3 = find(ypred==3);
figure,plot(Ax(indx1),Ay(indx1),'.','Color',[249/255 219/255 219/255],'LineWidth',6,'MarkerSize',20)
hold on;plot(Ax(indx2),Ay(indx2),'.','Color',[219/255 249/255 219/255],'LineWidth',6,'MarkerSize',20)
hold on;plot(Ax(indx3),Ay(indx3),'.','Color',[204/255 204/255 1],'LineWidth',6,'MarkerSize',20)
hold on;plot(X(1,inx1),X(2,inx1),'ro','LineWidth',2,'MarkerSize',8)
hold on;plot(X(1,inx2),X(2,inx2),'go','LineWidth',2,'MarkerSize',7)
hold on;plot(X(1,inx3),X(2,inx3),'bo','LineWidth',2,'MarkerSize',7)
hold on;contour(reshape(Ax,101,101), reshape(Ay,101,101),reshape(ypred,101,101),'LineColor','k','LineWidth',1.5);
hold on;contour(reshape(Ax,101,101), reshape(Ay,101,101),reshape(scores1,101,101),'LineColor','r','LineWidth',1.5);
hold on;contour(reshape(Ax,101,101), reshape(Ay,101,101),reshape(scores2,101,101),'LineColor','g','LineWidth',1.5);
hold on;contour(reshape(Ax,101,101), reshape(Ay,101,101),reshape(scores3,101,101),'LineColor','b','LineWidth',1.5);
title('SVM with Gaussian Kernel')
xlabel('Petal Width')
ylabel('Petal Length')
axis([0 3 0.5 7])