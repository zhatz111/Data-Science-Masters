function [a1p1, a2p1, a3p1, a1p2, a2p2, a3p2, a1p3, a2p3, a3p3] = ...
                                   hw3_confusion_matrix_3Class(predict, actual)
% This code will generate the confusion matrix for a three-class 
% classification problem. This code can be updated to fit any number of
% classes by using a structure or matrix to populate the values.

a1p1 = 0;
a2p1 = 0;
a3p1 = 0;
a1p2 = 0;
a2p2 = 0;
a3p2 = 0;
a1p3 = 0;
a2p3 = 0;
a3p3 = 0;

for i = 1:length(actual)
    if actual(i) == 1
        if predict(i) == 1
            a1p1 = a1p1 + 1;
        elseif predict(i) == 2
            a1p2 = a1p2 + 1;
        elseif predict(i) == 3
            a1p3 = a1p3 + 1;
        end
    elseif actual(i) == 2
        if predict(i) == 1
            a2p1 = a2p1 + 1;
        elseif predict(i) == 2
            a2p2 = a2p2 + 1;
        elseif predict(i) == 3
            a2p3 = a2p3 + 1;
        end
    elseif actual(i) == 3
        if predict(i) == 1
            a3p1 = a3p1 + 1;
        elseif predict(i) == 2
            a3p2 = a3p2 + 1;
        elseif predict(i) == 3
            a3p3 = a3p3 + 1;
        end
    end
end