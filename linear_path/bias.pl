% Learn to partition an input graph
% python hopper/popper.py --kbpath linear_path --max-ho 3 --max-rules 3

enable_recursion.

% Predicate declarations
head_pred(linearpath,2). 
body_pred(branches,1).
body_pred(not_branches,1).
body_pred(is_connected,2).
body_pred(same_gate,2).

% Types
type(linearpath,(element,element)). 
type(branches,(element,)).
type(not_branches,(element,)).
type(is_connected,(element,element)).
type(same_gate,(element,element)).

% Input-output signatures
direction(linearpath,(in,out)). 
direction(branches,(in,)).
direction(not_branches,(in,)).
direction(is_connected,(in,out)).
direction(same_gate,(in,out)).