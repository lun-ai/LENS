:- ['prim.pl'].
:- ['../partition/target.pl'].

% Given a fault, compute the minimum and maximum partition sizes
partition_sizes(A,B):- partition(A,E,C),size(C,F),size(E,D),pair(D,F,B).
partition_sizes(A,B):- partition(A,E,C),size(C,F),size(E,D),pair(F,D,B).