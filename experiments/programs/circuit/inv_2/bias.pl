% Predicate declarations
head_pred(inv_2,2). 
body_pred(inv_1,3).
body_pred(size,2).
body_pred(pair,3).

% Types
type(inv_2,(element,list)). 
type(inv_1,(element,list,list)).
type(size,(list,element)).
type(pair,(element,element,list)).

% Input-output signatures
direction(inv_2,(in,out)). 
direction(inv_1,(in,out,out)).
direction(size,(in,out)).
direction(pair,(in,in,out)).