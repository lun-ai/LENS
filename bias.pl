% Learn a divide and conquer strategy to partition each input graph
% python hopper/popper.py --kbpath . --max-ho 3

% max_body(12).

head_pred(select_test,2). 
body_pred(empty_partitions,1).
% body_pred(partition_sizes,2).
% body_pred(share_subpath,2).
% body_pred(n_subpath,2).
body_pred(partition,3).
body_pred(pair,3).
body_pred(max_min_size,3).
body_pred(map,3,ho).
body_pred(fold,4,ho).
body_pred(all,3,ho).

type(select_test,(list,list)). 
type(empty_partitions,(list,)).
% type(partition_sizes,(element,list)).
% type(share_subpath,(element,element)).
% type(n_subpath,(element,element)).
type(partition,(element,list,list)).
type(pair,(element,element,list)).
type(max_min_size,(list,list,list)).
type(map,((element,list),list,list)).
type(fold,((list,list,list),list,list,list)).
type(all,((element,element),element,list)).

direction(select_test,(in,out)). 
direction(empty_partitions,(out,)).
% direction(partition_sizes,(in,out)).
% direction(share_subpath,(in,out)).
% direction(n_subpath,(in,out)).
direction(partition,(in,out,out)).
direction(pair,(in,in,out)).
direction(max_min_size,(in,in,out)).
direction(map,((in,out),in,out)).
direction(fold,((in,in,out),in,in,out)).
direction(all,((in,in),in,out)).

% only_once(empty_partitions).
% only_once(max_min_size).
% only_once(partition).
% only_once(pair).

% :- 
    % body_literal(_,empty_partitions,_,Vars1), 
    % body_literal(_,empty_partitions,_,Vars2), 
    % Vars1 != Vars2.

:-  not body_literal(_,partition,3,_).
:-  not body_literal(_,pair,3,_).

% :-
%     only_once(P),
%     #count{Vars: body_literal(C,P,A,Vars)} > 1.