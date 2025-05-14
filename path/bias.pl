% Learn to partition an input graph
% python hopper/popper.py --kbpath path --max-ho 3 --max-rules 3

enable_recursion.

% Predicate declarations
head_pred(path,2). 
body_pred(is_connected,2).
body_pred(equal,2).

% Types
type(path,(element,element)). 
type(is_connected,(element,element)).
type(equal,(element,element)).

% Input-output signatures
direction(path,(in,out)). 
direction(is_connected,(in,out)).
direction(equal,(in,out)).