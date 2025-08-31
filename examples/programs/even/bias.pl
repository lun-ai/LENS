enable_recursion.

% Predicate declarations
head_pred(even,1). 
body_pred(pred,2).
body_pred(odd,1).

% Types
type(even,(element,)). 
type(pred,(element,element)).
type(odd,(element,)).

% Input-output signatures
direction(even,(in,)). 
direction(pred,(in,out)).
direction(odd,(in,)).