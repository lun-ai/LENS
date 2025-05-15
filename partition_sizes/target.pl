:- ['prim.pl'].
:- ['../partition/target.pl'].

% Given a fault, compute the partition sizes and write them into a pair
partition_sizes(A,B):- partition(A,C,D),size(C,E),size(D,F),pair(E,F,B).