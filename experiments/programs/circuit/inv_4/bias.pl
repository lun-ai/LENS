% Predicate declarations
head_pred(inv_4,2). 
body_pred(inv_3,2). 
body_pred(inv_2,2). 
body_pred(gate,1).
body_pred(test_point_label,2).

% Types
type(inv_4,(list,element)). 
type(inv_3,(list,list)). 
type(inv_2,(element,list)). 
type(gate,(element,)).
type(test_point_label,(element,element)).

% Input-output signatures
direction(inv_4,(in,out)). 
direction(inv_3,(in,out)). 
direction(inv_2,(in,out)). 
direction(gate,(out,)).
direction(test_point_label,(in,out)).

% Turn off invented predicates in HO
:- invented_ho_used(_,_).