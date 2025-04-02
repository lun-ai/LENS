:- ['prim.pl'].
:- ['../partition/target.pl'].

% Given a fault, zip the partition sizes into a pair
partition_sizes(A,B):- partition(A,E,C),size(C,F),size(E,D),pair(D,F,B).
partition_sizes(A,B):- partition(A,E,C),size(C,F),size(E,D),pair(F,D,B).