% This code is for educational and research purposes of comparisons. This
% is a Matlab SVM three class example using the iris data set. This example
% is from the Matlab documentation

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

figure,plot(iris_data.X(1:50,3),zeros(1,50),'ro','MarkerSize',8,'LineWidth',1.5)
hold on;plot(iris_data.X(51:100,3),zeros(1,50),'go','MarkerSize',8,'LineWidth',1.5)
hold on;plot(iris_data.X(101:150,3),zeros(1,50),'bo','MarkerSize',8,'LineWidth',1.5)

ax = 0:0.05:8; % used to test the space from 0 to 8 in increments of 0.05
hold on;plot(ax,zeros(1,length(ax)),'k','MarkerSize',8,'LineWidth',1.5)

SVMModels = cell(3,1);
classes = unique(iris_data.Y);
rng(1); % For reproducibility

for j = 1:numel(classes)
    indx = ismember(iris_data.Y,classes(j)); % Identifies the indicies for each classifier
    SVMModels{j} = fitcsvm(iris_data.X(:,3),indx,'ClassNames',...
                          [false true],'Standardize',true,...
                          'KernelFunction','gaussian','BoxConstraint',1);
end

for j = 1:numel(classes)
    [~,score] = predict(SVMModels{j},ax');
    Scores(:,j) = score(:,2); % Second column contains positive-class scores
end
[~,ypred] = max(Scores,[],2);

hold on,plot(ax,Scores(:,1),'r','MarkerSize',8,'LineWidth',1)
hold on,plot(ax,Scores(:,2),'g','LineWidth',1)
hold on,plot(ax,Scores(:,3),'b','LineWidth',1)


% add the support vectors
hold on,plot(iris_data.X(SVMModels{3,1}.IsSupportVector),zeros(1,length(iris_data.X(SVMModels{3,1}.IsSupportVector))),'ok','MarkerSize',12,'LineWidth',2)
