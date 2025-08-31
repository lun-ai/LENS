% Predicate declarations
head_pred(inv_1,3). 
body_pred(inv_0,2).
body_pred(not_inv_0,2).
body_pred(same_circuit,2).
body_pred(find_all,3,ho).

% Types
type(inv_1,(element,list,list)). 
type(inv_0,(element,element)).
type(not_inv_0,(element,element)).
type(same_circuit,(element,element)).
type(find_all,((element,element),element,list)).

% Input-output signatures
direction(inv_1,(in,out,out)). 
direction(inv_0,(in,out)).
direction(not_inv_0,(in,out)).
direction(same_circuit,(in,out)).
direction(find_all,((in,out),in,out)).

% Must use the following predicates
:- not body_literal(_,same_circuit,_,(0,1)).
:- not body_literal(_,inv_0,_,(1,0)).
:- not body_literal(_,not_inv_0,_,(1,0)).