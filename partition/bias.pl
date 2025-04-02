% Learn to partition an input graph
% python hopper/popper.py --kbpath partition --max-ho 3 --max-rules 3

% Predicate declarations
head_pred(partition,3). 
body_pred(linear_path,2).
body_pred(not_linear_path,2).
body_pred(same_circuit,2).
body_pred(all,3,ho).

% Types
type(partition,(element,list,list)). 
type(linear_path,(element,element)).
type(not_linear_path,(element,element)).
type(same_circuit,(element,element)).
type(all,((element,element),element,list)).

% Input-output signatures
direction(partition,(in,out,out)). 
direction(linear_path,(in,out)).
direction(not_linear_path,(in,out)).
direction(same_circuit,(in,out)).
direction(all,((in,out),in,out)).