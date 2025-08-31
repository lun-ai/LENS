enable_recursion.

% Predicate declarations
head_pred(inv_0,2). 
body_pred(is_equal,2).
body_pred(not_empty_list,1).
body_pred(is_connected,2).
body_pred(find_all,3,ho).
body_pred(all,3,ho).

% Types
type(inv_0,(element,element)). 
type(is_equal,(element,element)).
type(not_empty_list,(list,)).
type(is_connected,(element,element)).
type(find_all,((element,element),element,list)).
type(all,((element,element),list,element)).

% Input-output signatures
direction(inv_0,(in,out)). 
direction(is_equal,(in,out)).
direction(not_empty_list,(in,)).
direction(is_connected,(in,out)).
direction(find_all,((in,out),in,out)).
direction(all,((in,out),in,out)).

% Constraint the occurrence of predicates
occurFO(is_equal, 1).
occurFO(not_empty_list, 1).
occurFO(is_connected, 1).
occurHO(find_all,1).
occurHO(all, 1).
:-
    body_pred(X,_),
    #count{C,X,V: body_literal(C,X,_,V)} > Z, occurFO(X,Z).
:- 
    body_pred(X,_,ho), #count{C,Y,V:  body_literal(C,Y,_,V), X=@honameparse(Y)} >Z, occurHO(X,Z).

% Turn off invented predicates in HO
:- invented_ho_used(_,_).