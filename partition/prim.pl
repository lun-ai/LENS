% Does gate A share a linear path with gate B (B precedes A if A \== B)?
same_circuit(A, B) :- gate(A), gate(B), N is A // 100, M is B // 100, N == M.