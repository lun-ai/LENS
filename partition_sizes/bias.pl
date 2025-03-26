% Learn to compute sizes of partitions
% python hopper/popper.py --kbpath partition_sizes --max-rules 3

% Predicate declarations
head_pred(partition_sizes,2). 
body_pred(partition,3).
body_pred(size,2).
body_pred(min,3).
body_pred(max,3).
body_pred(pair,3).

% Types
type(partition_sizes,(element,list)). 
type(partition,(element,list,list)).
type(size,(list,element)).
type(min,(element,element,element)).
type(max,(element,element,element)).
type(pair,(element,element,list)).

% Input-output signatures
direction(partition_sizes,(in,out)). 
direction(partition,(in,out,out)).
direction(size,(in,out)).
direction(min,(in,in,out)).
direction(max,(in,in,out)).
direction(pair,(in,in,out)).