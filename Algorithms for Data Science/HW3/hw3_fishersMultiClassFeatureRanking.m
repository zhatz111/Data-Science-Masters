function model =  hw3_fishersMultiClassFeatureRanking(Data,method)
% This code has been modified from its original content for educational
% and research purposes of comparisons. Full credit is given to the  
% original referenced developer. 
%
% Calculates a Fisher/Correlation score for each feature and ranks the 
% features based on the correlation score.
% This works for either a two class or multi-class case
%
% Input:
%    data.X [dim x num_data] training vectors.
%    data.Y [1 x num_data] labels (class) of training data {1, 2, ...}
%    method [1 x 1] only for the multi-class case. This is how the scores 
%                   of the different one-vs-rest fisher's score are 
%                   conbined.
%                   1 = min
%                   2 = max
%                   3 = sum
%                   4 = average - (min+max)/2
% 
% Output:
%    model.featureIndex -- ranked feature indices
%    model.featureRankingMethod -- the feature ranking method used in this
%                                  case 'fishersMultiClassFeatureRanking'
%    model.rankValue -- The value used in ranking the features
%
% Example:
%
%
% Reference
%   Bishop, C. (1995). Neural Networks for Pattern Recognition
%   
%  V. Franc, Optimization Algorithms for Kernal Methods, (2005)
%  V. Franc, Statistical Pattern Recognition Toolbox, (2007)
%  https://cmp.felk.cvut.cz/cmp/software/stprtool/


X = Data.X; 

[numEx,vDim]=size(X);

Y = Data.Y;

oDim = max(Y);
alg.rank=[];

if oDim<2 % if two-class
    
    corr = zeros(vDim,1);
    corr = (mean(X(Y==1,:))-mean(X(Y==-1,:))).^2;
    st   = std(X(Y==1,:)).^2;
    st   = st+std(X(Y==-1,:)).^2;
    f=find(st==0);
    st(f)=10000;
    corr = corr ./ st;

    % features ranked based on the best correlation scores
    indx = find(abs(corr)>10000);
    corr(indx) = 0;
    [values rankIndx] = sort(-abs(corr));

    model.featureIndex = rankIndx;
    model.rankValue = values;
    model.featureRankingMethod = 'fishersFeatureRanking';

else %% if oDim>=2...
    Std = zeros(1,vDim);
    for i=1:oDim
        indQ = find(Y == i);
        Std = Std + std(X(indQ,:),1);
    end
    for i=1:oDim
        indp = find(Y == i);
        Wtmp(:,i) = (mean(X(indp,:))./Std)';
    end
    indTemp=[];
    corrTemp=[];
    for j=1:oDim
        WW = [Wtmp(:,1:j-1),Wtmp(:,j+1:oDim)];
        WW = (Wtmp(:,j)*ones(1,oDim-1) - WW);
        switch method
            case 1
                rankW = min(WW,[],2);
            case 2
                rankW = max(WW,[],2);
            case 3
                rankW = sum(WW')';
            case 4
                r1 = min(WW,[],2);
                r2 = max(WW,[],2);
                rankW = (r1 + r2)/2;
        end
        [u,v] = sort(-abs(rankW'));
        indTemp = [indTemp,v'];
        corrTemp = [corrTemp, u'];
    end

    indTemp = reshape(indTemp',1,oDim*vDim);
    corrTemp = reshape(corrTemp',1,oDim*vDim);
    
    [corrSort indx] = sort(corrTemp);
    indxSort = indTemp(indx);
    indTemp = fliplr(indxSort);
    corrTemp = fliplr(corrSort);

    [u,v] = unique(indTemp);
    [w,s] = sort(v);
    values = fliplr(corrTemp(w));
    rankIndx = fliplr(u(s));

    model.featureIndex = rankIndx;
    model.rankValue = values;
    model.featureRankingMethod = 'fishersMultiClassFeatureRanking';
end
