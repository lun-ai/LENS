:- ['prim.pl'].
:- ['../partition/target.pl'].

% Given a fault, compute the minimum and maximum partition sizes
% partition_sizes(F, S) :- partition(F, P1, P2),
                        %  size(P1, L1), 
                        %  size(P2, L2), 
                        %  min(L1, L2, Min),
                        %  max(L1, L2, Max),
%                          pair(Min, Max, S).

partition_sizes(A,B):- partition(A,E,C),size(C,F),size(E,D),pair(D,F,B).
partition_sizes(A,B):- partition(A,E,C),size(C,F),size(E,D),pair(F,D,B).