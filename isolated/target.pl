:- ['prim.pl'].

isolated(A,B):- equal(A,B).
isolated(A,B):- find_all(is_connected,A,C),not(empty(C)),all(isolated,C,B).

not_isolated(A,B):- not(isolated(A,B)).