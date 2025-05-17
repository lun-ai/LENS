:- ['prim.pl'].

isolated_behind(A,B):- equal(A,B).
isolated_behind(A,B):- find_all(is_connected,A,C),not(empty(C)),all(isolated_behind,C,B).

not_isolated_behind(A,B):- not(isolated_behind(A,B)).