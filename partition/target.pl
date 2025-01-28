:- ['prim.pl'].

% Gates affected by a test and those not affected
inv_ho_1(A,B):- same_circuit(A,B),not(subpath(B,A)).
inv_ho_0(A,B):- same_circuit(A,B),subpath(B,A).

% A gate F partitions the circuit: gates on the same branch as F and gates on different branches
partition(A,B,C):- all(inv_ho_0,A,B),all(inv_ho_1,A,C).