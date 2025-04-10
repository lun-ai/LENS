:- ['prim.pl'].

% Given Gate A, find gates on the same linear path as A
inv_ho_0(A,B):- same_circuit(A,B),linearpath(B,A).
% Given Gate A, find gates on other paths
inv_ho_1(A,B):- same_circuit(A,B),not(linearpath(B,A)).

% Partition gates into two groups. Given Gate A, find gates on the same linear path as A and gates on other paths
partition(A,B,C):- all(inv_ho_0,A,B),all(inv_ho_1,A,C).