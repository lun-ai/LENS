:- ['all_bk.pl'].
:- ['ex_bk.pl'].

% V1 arguments are tuples
% select_test((+Faults, +Size, +Test), (?Faults1, ?Size1, ?Test1))
% select_test(In, Out) :- fst(In, L), empty(L), eq(In, Out). 
% select_test(In, Out) :- head_fault(In, F), min_partition_size(F, K), snd(In, N), gt(K, N), tail_faults(In, Fs), out(F, O), update_all(In, Fs, K, O, In1), select_test(In1, Out).
% select_test(In, Out) :- head_fault(In, F), min_partition_size(F, K), snd(In, N), leq(K, N), tail_faults(In, Fs), update_fst(In, Fs, In1), select_test(In1, Out).

% V2 
% select_test(+Faults, ?Size, ?Test)
% select_test(Faults, Size, Test) :- empty(Faults), zero(Size), gate(Test). 
% select_test(Faults, Size, Test) :- head(Faults, Test), tail(Faults, Fs), 
%                                    select_test(Fs, K, T), gate(T), 
%                                    min_partition_size(Test, Size), gt(Size, K).
% select_test(Faults, Size, Test) :- head(Faults, T), tail(Faults, Fs), 
%                                    select_test(Fs, Size, Test),  
%                                    min_partition_size(T, K), leq(K, Size).

% V3
% select_test(+Faults, ?Partition_sizes)
% select_test(Faults, Partition_sizes) :- empty(Faults), empty_partitions(Partition_sizes).
% select_test(Faults, Partition_sizes) :- head(Faults, Test), tail(Faults, Fs), 
%                                         select_test(Fs, P1),
%                                         partition_sizes(Test, P2),
%                                         max_min_size(P1, P2, Partition_sizes).

% V4 with abstractions
% select_test(+Faults, ?Partition_sizes)
select_test(Faults, PartitionSizes) :- map(partition_sizes, Faults, Partitions), 
                                        empty_partitions(V),
                                        fold(max_min_size, V, Partitions, PartitionSizes).

% Learned hypotheses
% select_test(A,B):- empty_partitions(C),map(partition_sizes,A,D),fold(max_min_size,C,D,B).                                    