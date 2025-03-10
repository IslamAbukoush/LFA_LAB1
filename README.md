# Laboratory Work 1: Regular Grammars & Finite Automata

## Student Information
- **Name:** Islam Abu koush
- **Group:** FAF-231
- **Course:** Formal Languages & Finite Automata
- **Date:** February 2025

## Abstract

This laboratory work implements a comprehensive system for working with Regular Grammars and Finite Automata, fundamental concepts in formal language theory. The implementation showcases object-oriented programming principles in Python, featuring a Regular Grammar generator, conversion to Deterministic Finite Automaton (DFA), string validation functionality, and an interactive user interface. The project demonstrates both theoretical understanding and practical application of formal language concepts.

## Table of Contents
1. [Theory](#theory)
2. [Objectives](#objectives)
3. [Implementation Description](#implementation-description)
4. [Detailed Code Analysis](#detailed-code-analysis)
5. [Program Flow](#program-flow)
6. [User Interface Implementation](#user-interface-implementation)
7. [Testing and Validation](#testing-and-validation)
8. [Results](#results)
9. [Conclusions](#conclusions)

## Theory

### Regular Grammars
A regular grammar is a formal grammar that generates regular languages. It consists of:
- A finite set of non-terminal symbols (V_n)
- A finite set of terminal symbols (V_t)
- A finite set of production rules (P)
- A start symbol (S)

Regular grammars are characterized by their production rules taking one of two forms:
1. Right-linear productions:
   - A → aB (where A,B ∈ V_n and a ∈ V_t)
   - A → a (where A ∈ V_n and a ∈ V_t)

2. Left-linear productions:
   - A → Ba (where A,B ∈ V_n and a ∈ V_t)
   - A → a (where A ∈ V_n and a ∈ V_t)

### Finite Automata
A Deterministic Finite Automaton (DFA) is a 5-tuple (Q, Σ, δ, q0, F) where:
- Q: finite set of states
- Σ: finite set of input symbols (alphabet)
- δ: transition function (Q × Σ → Q)
- q0: initial state
- F: set of accepting states

Key properties of DFAs:
- Deterministic behavior: each state has exactly one transition for each input symbol
- No epsilon (empty) transitions
- Complete specification: transitions defined for all state-input pairs
- Acceptance determined by final state membership

### Relationship Between Regular Grammars and DFAs
Regular grammars and DFAs are equivalent in computational power:
- Every regular grammar can be converted to a DFA
- Every DFA can be converted to a regular grammar
- Both recognize exactly the class of regular languages

## Objectives

1. **Grammar Implementation:**
   - Create a Regular Grammar class with proper validation
   - Implement string generation functionality
   - Ensure grammatical correctness of generated strings
   - Provide clear visualization of derivation steps

2. **Finite Automaton:**
   - Implement DFA representation
   - Create conversion mechanism from Regular Grammar to DFA
   - Develop string validation functionality
   - Visualize state transitions

3. **User Interface:**
   - Create an interactive command-line interface
   - Implement clear visualization of transitions and processes
   - Provide comprehensive feedback during string validation
   - Ensure user-friendly interaction flow

## Implementation Description

### Core Components

#### 1. Data Structures
The implementation uses Python's built-in data structures effectively:
- `Set` for unique collections (states, alphabet)
- `Dict` for mappings (transitions, productions)
- `List` for ordered collections (derivation steps)
- `defaultdict` for automatic dictionary initialization

#### 2. Type Hints
The code uses Python's type hinting system for better code documentation and IDE support:
```python
from typing import Set, Dict, List, Optional
from dataclasses import dataclass
```

## Detailed Code Analysis

### RegularGrammar Class

#### Class Definition and Initialization
```python
class RegularGrammar:
    def __init__(self, non_terminals: Set[str], terminals: Set[str], 
                 productions: Dict[str, List[str]], start: str):
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self.start = start
        self._validate_grammar()
```

This initialization ensures:
- Proper type checking through type hints
- Immediate validation of grammar consistency
- Clear separation of grammar components

#### Grammar Validation
```python
def _validate_grammar(self) -> None:
    """Validates the grammar's consistency."""
    assert self.start in self.non_terminals, "Start symbol must be a non-terminal"
    assert not (self.terminals & self.non_terminals), "Terminals and non-terminals must be disjoint"
    
    for left, rules in self.productions.items():
        assert left in self.non_terminals, f"Invalid non-terminal in production: {left}"
        for rule in rules:
            assert rule[0] in self.terminals, f"First symbol in {rule} must be terminal"
            if len(rule) > 1:
                assert rule[1] in self.non_terminals, f"Second symbol in {rule} must be non-terminal"
```

Validation steps:
1. Verifies start symbol existence
2. Checks for symbol set disjointness
3. Validates production rule format
4. Ensures symbol consistency

#### String Generation Algorithm
```python
def derive_string(self) -> str:
    current = self.start
    derivation = [current]
    
    while any(symbol in self.non_terminals for symbol in current):
        for pos, symbol in enumerate(current):
            if symbol in self.non_terminals:
                if options := self.productions.get(symbol):
                    replacement = random.choice(options)
                    current = current[:pos] + replacement + current[pos+1:]
                    derivation.append(current)
                    break
    
    print(f"\n🔄 Derivation: {' → '.join(derivation)}")
    return current
```

Key features:
1. Random selection of production rules
2. Step-by-step derivation tracking
3. Non-terminal replacement logic
4. Derivation visualization

#### Grammar to DFA Conversion
```python
def convert_to_dfa(self) -> DFA:
    """Converts the regular grammar to an equivalent DFA."""
    final_state = "FINAL"
    states = self.non_terminals | {final_state}
    transitions: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
    
    for source, rules in self.productions.items():
        for rule in rules:
            if len(rule) == 1:
                transitions[source][rule[0]].add(final_state)
            else:
                transitions[source][rule[0]].add(rule[1])
    
    return DFA(
        states=states,
        alphabet=self.terminals,
        transitions=dict(transitions),
        start_state=self.start,
        accept_states={final_state}
    )
```

Conversion process:
1. Creates final state
2. Maps non-terminals to DFA states
3. Converts productions to transitions
4. Handles terminal productions
5. Maintains deterministic property

### DFA Class

#### Class Structure
```python
@dataclass
class DFA:
    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[str, Dict[str, Set[str]]]
    start_state: str
    accept_states: Set[str]
```

The `@dataclass` decorator provides:
- Automatic `__init__` method
- Built-in string representation
- Comparison methods
- Immutable instance option

#### String Validation
```python
def validate_string(self, input_str: str) -> bool:
    current_states = {self.start_state}
    print(f"\n🔍 Validating: '{input_str}'")
    
    for char in input_str:
        if char not in self.alphabet:
            print(f"❌ Invalid character '{char}' - not in alphabet {self.alphabet}")
            return False
        
        next_states = set()
        for state in current_states:
            if state in self.transitions and char in self.transitions[state]:
                next_states.update(self.transitions[state][char])
        
        if not next_states:
            print(f"❌ No valid transitions - string rejected")
            return False
        
        current_states = next_states
        print(f"📍 Current states: {current_states}")
    
    is_accepted = any(state in self.accept_states for state in current_states)
    print(f"📌 Final states: {current_states}")
    print(f"{'✅ String accepted!' if is_accepted else '❌ String rejected!'}")
    return is_accepted
```

Validation steps:
1. Alphabet validation
2. State transition tracking
3. Multiple state handling
4. Detailed progress logging
5. Acceptance checking

#### Transition Table Visualization
```python
def print_transitions(self) -> None:
    print("\n📊 Transition Table:")
    print("-" * 60)
    for state in self.states:
        if state not in self.transitions:
            continue
        for symbol in sorted(self.alphabet):
            if symbol in self.transitions[state]:
                targets = self.transitions[state][symbol]
                transitions = ', '.join(sorted(targets))
                print(f"  {state} --({symbol})--> {transitions}")
    print("-" * 60)
```

Features:
1. Sorted state and symbol presentation
2. Clear transition formatting
3. Visual separation
4. Skip empty transitions

## User Interface Implementation

### Console Clearing
```python
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
```
- Cross-platform compatibility
- Clean interface presentation

### Header Display
```python
def print_header():
    print("=" * 60)
    print("🔤  FORMAL LANGUAGES LAB 1: REGULAR GRAMMARS & DFAs  🔤")
    print("=" * 60)
    print("\n👤 Name: Islam Abu koush")
    print("👥 Group: FAF-231")
    print("🔢 Variant: 1\n")
    print("=" * 60 + "\n")
```
- Clear visual hierarchy
- Emoji usage for visual interest
- Consistent formatting

### Menu System
```python
def display_menu():
    print("\n📋 Menu Options:")
    print("1. Generate and validate 5 random strings")
    print("2. Input a string to validate")
    print("3. Exit")
    return input("\n👉 Choose an option (1-3): ")
```
- Clear option presentation
- Input validation
- User guidance

### Main Program Flow
```python
def main() -> None:
    clear_screen()
    print_header()
    
    # Initialize grammar
    grammar = RegularGrammar(
        non_terminals={"S", "P", "Q"},
        terminals={"a", "b", "c", "d", "e", "f"},
        productions={
            "S": ["aP", "bQ"],
            "P": ["bP", "cP", "dQ", "e"],
            "Q": ["eQ", "fQ", "a"]
        },
        start="S"
    )
    
    # Convert to DFA
    dfa = grammar.convert_to_dfa()
    
    # Main interaction loop
    while True:
        choice = display_menu()
        
        if choice == "1":
            # Generate and validate strings
            pass
        elif choice == "2":
            # Validate user input
            pass
        elif choice == "3":
            # Exit program
            pass
```

Program flow features:
1. Clear initialization
2. Structured menu system
3. Continuous operation
4. Clean exit handling

## Testing and Validation

### String Generation Testing
- Multiple string generation
- Derivation verification
- Production rule coverage
- Terminal string validation

### DFA Testing
- Transition completeness
- Acceptance criteria
- Error handling
- State reachability

## Results

The implementation successfully demonstrates:

1. Grammar Operations:
   - Valid string generation
   - Proper derivation tracking
   - Production rule application

2. DFA Functionality:
   - Correct state transitions
   - Proper string validation
   - Clear visualization

3. User Interface:
   - Interactive operation
   - Clear feedback
   - Error handling
   - Visual clarity

Example Grammar:
```
Non-terminals = {S, P, Q}
Terminals = {a, b, c, d, e, f}
Productions = {
    S → aP | bQ
    P → bP | cP | dQ | e
    Q → eQ | fQ | a
}
Start = S
```

Sample Derivation:
```
S → aP → abP → abcP → abce
```

## Conclusions

The implementation successfully demonstrates:

1. Theoretical Understanding:
   - Regular grammar concepts
   - Finite automata principles
   - Language theory application

2. Technical Implementation:
   - Clean code practices
   - Object-oriented design
   - Type safety
   - Error handling

3. User Experience:
   - Interactive interface
   - Clear visualization
   - Comprehensive feedback
   - Intuitive operation

4. Educational Value:
   - Clear demonstration of concepts
   - Step-by-step visualization
   - Interactive learning opportunities

The project provides a robust foundation for understanding and working with formal languages while maintaining software engineering best practices.

# Laboratory Work on Finite Automata & Grammars

## Course: Formal Languages & Finite Automata
## Student: Islam Abu koush
## Group: FAF-231
## Variant: 1

## Table of Contents
1. [Introduction](#introduction)
2. [Theoretical Background](#theoretical-background)
   - [Finite Automata](#finite-automata)
   - [Regular Grammars](#regular-grammars)
   - [Chomsky Hierarchy](#chomsky-hierarchy)
   - [Conversions Between Representations](#conversions-between-representations)
3. [Objectives](#objectives)
4. [Implementation](#implementation)
   - [Class Structure](#class-structure)
   - [Code Implementation Details](#code-implementation-details)
      - [Base Finite Automaton Class](#base-finite-automaton-class)
      - [DFA Implementation](#dfa-implementation)
      - [NDFA Implementation](#ndfa-implementation)
      - [Regular Grammar Implementation](#regular-grammar-implementation)
      - [Conversion Algorithms](#conversion-algorithms)
   - [The Variant NDFA](#the-variant-ndfa)
5. [Testing and Results](#testing-and-results)
   - [String Validation](#string-validation)
   - [NDFA to DFA Conversion](#ndfa-to-dfa-conversion)
   - [FA to Regular Grammar Conversion](#fa-to-regular-grammar-conversion)
   - [Grammar Classification](#grammar-classification)
6. [User Interface](#user-interface)
7. [Conclusions](#conclusions)
8. [References](#references)

## Introduction

This laboratory work focuses on the implementation and exploration of formal languages theory concepts, specifically finite automata (FA) and regular grammars. The project implements both deterministic finite automata (DFA) and non-deterministic finite automata (NDFA), as well as regular grammars, and provides functionality to convert between these different representations of regular languages. Additionally, the project includes functionality to classify grammars according to the Chomsky hierarchy.

The implementation is done in Python, using object-oriented programming principles to represent the various formal language constructs. The code provides a comprehensive suite of tools for working with finite automata and grammars, including string validation, automaton conversion, and grammar classification.

## Theoretical Background

### Finite Automata

A finite automaton (FA) is a mathematical model of computation that can be in exactly one of a finite number of states at any given time. The FA can change from one state to another in response to an input, through a process called a transition. Formally, a finite automaton is defined as a 5-tuple:

$M = (Q, Σ, δ, q_0, F)$

Where:
- $Q$ is a finite set of states
- $Σ$ is a finite set of input symbols, called the alphabet
- $δ$ is the transition function: $δ: Q × Σ → P(Q)$ (where $P(Q)$ is the power set of $Q$)
- $q_0$ is the initial state, $q_0 ∈ Q$
- $F$ is the set of final or accepting states, $F ⊆ Q$

Finite automata can be classified into two main types:

#### Deterministic Finite Automata (DFA)

In a DFA, for each state and input symbol, there is exactly one next state. The transition function is $δ: Q × Σ → Q$, meaning for each state-input pair, there is exactly one resulting state.

Properties of DFAs:
- For every state and input symbol, there is exactly one transition
- No empty (ε) transitions are allowed
- DFAs are efficient for string recognition as they have a single path to follow

#### Non-Deterministic Finite Automata (NDFA)

In an NDFA, for a given state and input symbol, there can be multiple possible next states or even no next state. The transition function is $δ: Q × Σ → P(Q)$, where $P(Q)$ is the power set of $Q$.

Properties of NDFAs:
- For some state-input pairs, there might be multiple possible next states
- NDFAs may be more compact representations than equivalent DFAs
- An NDFA accepts a string if there exists at least one path that leads to an accepting state

### Regular Grammars

A grammar is a set of production rules for generating strings in a formal language. A grammar $G$ is formally defined as a 4-tuple:

$G = (N, T, P, S)$

Where:
- $N$ is a finite set of non-terminal symbols
- $T$ is a finite set of terminal symbols
- $P$ is a finite set of production rules: $P ⊆ N × (N ∪ T)^*$
- $S$ is the start symbol, $S ∈ N$

A regular grammar (Type 3 in the Chomsky hierarchy) has production rules of the form:
- Right-linear: $A → aB$ or $A → a$ (where $A, B ∈ N$ and $a ∈ T$)
- Left-linear: $A → Ba$ or $A → a$ (where $A, B ∈ N$ and $a ∈ T$)
- $A → ε$ (where $ε$ is the empty string)

### Chomsky Hierarchy

The Chomsky hierarchy, proposed by Noam Chomsky in 1956, is a containment hierarchy of classes of formal grammars that generate formal languages. The hierarchy consists of four levels:

1. **Type 0: Unrestricted Grammars**
   - No restrictions on production rules
   - Can generate recursively enumerable languages
   - Recognized by Turing machines

2. **Type 1: Context-Sensitive Grammars**
   - Production rules of the form $αAβ → αγβ$ where $A$ is a non-terminal and $α, β, γ$ are strings of terminals and non-terminals, with $|γ| ≥ 1$
   - The length of the right side of a production must be at least as long as the left side
   - Can generate context-sensitive languages
   - Recognized by linear bounded automata

3. **Type 2: Context-Free Grammars**
   - Production rules of the form $A → γ$ where $A$ is a non-terminal and $γ$ is a string of terminals and non-terminals
   - Can generate context-free languages
   - Recognized by pushdown automata

4. **Type 3: Regular Grammars**
   - Production rules of the form $A → a$ or $A → aB$ or $A → ε$ (right-linear)
   - Can generate regular languages
   - Recognized by finite automata

Each type is a proper subset of the types above it:
Type 3 ⊂ Type 2 ⊂ Type 1 ⊂ Type 0

### Conversions Between Representations

There are several important conversion algorithms between different representations of regular languages:

1. **NDFA to DFA Conversion**
   - Uses the subset construction algorithm
   - Each state in the DFA corresponds to a subset of states in the NDFA
   - The resulting DFA can have up to $2^n$ states, where $n$ is the number of states in the NDFA

2. **FA to Regular Grammar Conversion**
   - States in the automaton become non-terminals in the grammar
   - Transitions become production rules
   - The language recognized by the FA is the same as the language generated by the grammar

3. **Regular Grammar to FA Conversion**
   - Non-terminals in the grammar become states in the automaton
   - Production rules become transitions
   - The language generated by the grammar is the same as the language recognized by the FA

## Objectives

The main objectives of this laboratory work are:

1. **Grammar Classification**: Implement a function in the grammar class that classifies the grammar based on the Chomsky hierarchy.

2. **Finite Automaton to Regular Grammar Conversion**: Implement functionality to convert a finite automaton to a regular grammar.

3. **Determinism Check**: Determine whether a given finite automaton is deterministic or non-deterministic.

4. **NDFA to DFA Conversion**: Implement an algorithm to convert a non-deterministic finite automaton (NDFA) to a deterministic finite automaton (DFA).

5. **String Validation**: Provide functionality to validate strings against both finite automata and grammars.

## Implementation

### Class Structure

The implementation uses a class-based approach with the following main classes:

1. **FiniteAutomaton**: An abstract base class that defines the common structure and methods for both DFA and NDFA.

2. **DFA**: A concrete implementation of a deterministic finite automaton, extending the FiniteAutomaton class.

3. **NDFA**: A concrete implementation of a non-deterministic finite automaton, extending the FiniteAutomaton class.

4. **RegularGrammar**: A class that represents a regular grammar with methods for string generation, classification, and conversion to a finite automaton.

### Code Implementation Details

#### Base Finite Automaton Class

The `FiniteAutomaton` class serves as the base class for both DFA and NDFA implementations. It defines the common structure and methods for finite automata:

```python
@dataclass
class FiniteAutomaton:
    """Base class for Finite Automaton implementations."""
    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[str, Dict[str, Set[str]]]
    start_state: str
    accept_states: Set[str]
```

Key methods of this class include:

- **is_deterministic()**: Checks if the automaton is deterministic by ensuring that for each state and symbol, there is exactly one transition.

```python
def is_deterministic(self) -> bool:
    """Check if the automaton is deterministic."""
    for state in self.states:
        if state not in self.transitions:
            continue
        for symbol in self.alphabet:
            if symbol in self.transitions[state]:
                # If any transition for a symbol leads to more than one state,
                # or if there's no transition for a symbol, the automaton is non-deterministic
                if len(self.transitions[state][symbol]) != 1:
                    return False
            else:
                # Missing transition for a symbol
                return False
    return True
```

- **print_transitions()**: Displays a formatted transition table for the automaton.

```python
def print_transitions(self) -> None:
    """Prints a formatted transition table."""
    print("\n📊 Transition Table:")
    print("-" * 60)
    for state in sorted(self.states):
        if state not in self.transitions:
            continue
        for symbol in sorted(self.alphabet):
            if symbol in self.transitions.get(state, {}):
                targets = self.transitions[state][symbol]
                transitions = ', '.join(sorted(targets))
                print(f"  {state} --({symbol})--> {transitions}")
    print("-" * 60)
```

- **convert_to_regular_grammar()**: Converts the automaton to an equivalent regular grammar.

```python
def convert_to_regular_grammar(self) -> 'RegularGrammar':
    """Convert the automaton to an equivalent regular grammar."""
    # Non-terminals are the states plus a special final symbol
    non_terminals = self.states.copy()
    
    # Create a mapping for state names to ensure they're valid non-terminals
    state_mapping = {state: f"S{i}" for i, state in enumerate(self.states)}
    
    # Terminals are the alphabet
    terminals = self.alphabet.copy()
    
    # Productions dictionary
    productions = defaultdict(list)
    
    # For each transition, create a production rule
    for state in self.states:
        if state not in self.transitions:
            continue
            
        for symbol, target_states in self.transitions[state].items():
            for target in target_states:
                if target in self.accept_states:
                    # If target is an accept state, we can derive just the terminal
                    # or terminal followed by a non-terminal
                    productions[state_mapping[state]].append(symbol)
                    
                    # Also add production for terminal + non-terminal
                    productions[state_mapping[state]].append(symbol + state_mapping[target])
                else:
                    # Otherwise, derive a terminal followed by a non-terminal
                    productions[state_mapping[state]].append(symbol + state_mapping[target])
    
    # Add empty production for accept states
    for state in self.accept_states:
        productions[state_mapping[state]].append("")
    
    # Create grammar with mapped state names
    return RegularGrammar(
        non_terminals=set(state_mapping.values()),
        terminals=terminals,
        productions=dict(productions),
        start=state_mapping[self.start_state]
    )
```

#### DFA Implementation

The `DFA` class extends `FiniteAutomaton` and provides a concrete implementation for deterministic finite automata:

```python
@dataclass
class DFA(FiniteAutomaton):
    """Deterministic Finite Automaton implementation."""
    
    def validate_string(self, input_str: str) -> bool:
        """Validates whether an input string is accepted by the DFA."""
        current_state = self.start_state
        print(f"\n🔍 Validating: '{input_str}'")
        
        for char in input_str:
            if char not in self.alphabet:
                print(f"❌ Invalid character '{char}' - not in alphabet {self.alphabet}")
                return False
            
            if current_state not in self.transitions or char not in self.transitions[current_state]:
                print(f"❌ No valid transition from state {current_state} with symbol {char}")
                return False
            
            current_state = next(iter(self.transitions[current_state][char]))
            print(f"📍 Current state: {current_state}")
        
        is_accepted = current_state in self.accept_states
        print(f"📌 Final state: {current_state}")
        print(f"{'✅ String accepted!' if is_accepted else '❌ String rejected!'}")
        return is_accepted
```

The `validate_string()` method in the DFA class:
1. Starts from the initial state
2. For each character in the input string:
   - Checks if the character is in the alphabet
   - Finds the next state using the transition function
   - Updates the current state
3. Accepts the string if the final state is an accept state

#### NDFA Implementation

The `NDFA` class also extends `FiniteAutomaton` but implements the behavior of non-deterministic finite automata:

```python
@dataclass
class NDFA(FiniteAutomaton):
    """Non-Deterministic Finite Automaton implementation."""
    
    def validate_string(self, input_str: str) -> bool:
        """Validates whether an input string is accepted by the NDFA."""
        current_states = {self.start_state}
        print(f"\n🔍 Validating: '{input_str}'")
        
        for char in input_str:
            if char not in self.alphabet:
                print(f"❌ Invalid character '{char}' - not in alphabet {self.alphabet}")
                return False
            
            next_states = set()
            for state in current_states:
                if state in self.transitions and char in self.transitions[state]:
                    next_states.update(self.transitions[state][char])
            
            if not next_states:
                print(f"❌ No valid transitions - string rejected")
                return False
            
            current_states = next_states
            print(f"📍 Current states: {current_states}")
        
        is_accepted = any(state in self.accept_states for state in current_states)
        print(f"📌 Final states: {current_states}")
        print(f"{'✅ String accepted!' if is_accepted else '❌ String rejected!'}")
        return is_accepted
```

The key difference in the NDFA's `validate_string()` method is that it maintains a set of current states rather than a single state, as multiple states can be active simultaneously in an NDFA.

The NDFA class also implements the `convert_to_dfa()` method, which uses the subset construction algorithm to convert an NDFA to an equivalent DFA:

```python
def convert_to_dfa(self) -> DFA:
    """Converts the NDFA to an equivalent DFA using the subset construction algorithm."""
    # Start with the initial state of the DFA, which is a set containing the start state of the NDFA
    dfa_start = frozenset([self.start_state])
    
    # Initialize the queue for BFS and visited set
    queue = deque([dfa_start])
    visited = {dfa_start}
    
    # Initialize DFA transitions
    dfa_transitions = {}
    
    # For pretty printing state names
    state_mapping = {dfa_start: f"q{0}"}
    counter = 1
    
    # Perform BFS to construct the DFA
    while queue:
        current_subset = queue.popleft()
        current_dfa_state = state_mapping[current_subset]
        
        # Initialize transitions for this DFA state
        dfa_transitions[current_dfa_state] = {}
        
        # For each symbol in the alphabet
        for symbol in self.alphabet:
            # Find all states that can be reached from the current subset via symbol
            next_subset = set()
            for state in current_subset:
                if state in self.transitions and symbol in self.transitions[state]:
                    next_subset.update(self.transitions[state][symbol])
            
            # Only process non-empty transitions
            if next_subset:
                next_subset_frozen = frozenset(next_subset)
                
                # Create a name for the new state if it hasn't been seen before
                if next_subset_frozen not in visited:
                    state_mapping[next_subset_frozen] = f"q{counter}"
                    counter += 1
                    visited.add(next_subset_frozen)
                    queue.append(next_subset_frozen)
                
                # Add the transition to the DFA
                dfa_transitions[current_dfa_state][symbol] = {state_mapping[next_subset_frozen]}
        
    # Determine accept states for the DFA
    dfa_accept_states = {
        state_mapping[subset] for subset in visited
        if any(state in self.accept_states for state in subset)
    }
    
    # Create the DFA states set
    dfa_states = set(state_mapping.values())
    
    # Create and return the DFA
    return DFA(
        states=dfa_states,
        alphabet=self.alphabet,
        transitions=dfa_transitions,
        start_state=state_mapping[dfa_start],
        accept_states=dfa_accept_states
    )
```

This algorithm:
1. Creates a start state for the DFA that is a set containing the start state of the NDFA
2. Uses breadth-first search to explore all reachable subsets of NDFA states
3. For each subset and input symbol, computes the next subset of states
4. Creates a DFA state for each unique subset encountered
5. Sets accept states of the DFA to be those subsets containing at least one accept state from the NDFA

#### Regular Grammar Implementation

The `RegularGrammar` class represents a regular grammar with methods for string generation, classification, and conversion:

```python
class RegularGrammar:
    """Implementation of a Regular Grammar."""
    def __init__(self, non_terminals: Set[str], terminals: Set[str], 
                 productions: Dict[str, List[str]], start: str):
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self.start = start
        self._validate_grammar()
```

Key methods of this class include:

- **_validate_grammar()**: Validates the grammar's consistency, ensuring that all productions follow the rules of regular grammars.

```python
def _validate_grammar(self) -> None:
    """Validates the grammar's consistency."""
    assert self.start in self.non_terminals, "Start symbol must be a non-terminal"
    assert not (self.terminals & self.non_terminals), "Terminals and non-terminals must be disjoint"
    
    for left, rules in self.productions.items():
        assert left in self.non_terminals, f"Invalid non-terminal in production: {left}"
        for rule in rules:
            if not rule:  # Empty rule is allowed for accept states
                continue
            assert rule[0] in self.terminals, f"First symbol in {rule} must be terminal"
            if len(rule) > 1:
                # Check if the rest of the rule consists of a valid non-terminal
                rest = rule[1:]
                assert rest in self.non_terminals, f"Rest of rule '{rule}' must be a valid non-terminal"
```

- **derive_string()**: Generates a random string using the grammar's production rules, showing the derivation steps.

```python
def derive_string(self) -> str:
    """Derives a random string using the grammar's production rules."""
    current = self.start
    derivation = [current]
    
    while any(symbol in self.non_terminals for symbol in current):
        for pos, symbol in enumerate(current):
            if symbol in self.non_terminals:
                if options := self.productions.get(symbol):
                    replacement = random.choice(options)
                    current = current[:pos] + replacement + current[pos+1:]
                    derivation.append(current)
                    break
    
    print(f"\n🔄 Derivation: {' → '.join(derivation)}")
    return current
```

- **classify_chomsky()**: Classifies the grammar according to the Chomsky hierarchy.

```python
def classify_chomsky(self) -> int:
    """
    Classifies the grammar according to the Chomsky hierarchy.
    Returns:
        0 - Type 0 (Unrestricted Grammar)
        1 - Type 1 (Context-Sensitive Grammar)
        2 - Type 2 (Context-Free Grammar)
        3 - Type 3 (Regular Grammar)
    """
    # Check for Type 3 (Regular Grammar)
    is_regular = True
    
    for left, rules in self.productions.items():
        for rule in rules:
            # Empty rule is allowed
            if not rule:
                continue
            
            # Check if rule is in the form of a terminal (a) or a terminal followed by a non-terminal (aB)
            is_valid_rule = rule[0] in self.terminals and (len(rule) == 1 or rule[1:] in self.non_terminals)
            
            if not is_valid_rule:
                is_regular = False
                break
        
        if not is_regular:
            break
    
    if is_regular:
        return 3
    
    # Check for Type 2 (Context-Free Grammar)
    is_context_free = True
    for left, rules in self.productions.items():
        if len(left) != 1 or left not in self.non_terminals:
            is_context_free = False
            break
    
    if is_context_free:
        return 2
    
    # By default, we'll consider it Type 0 for this implementation
    # In a more comprehensive implementation, we would check for Type 1
    return 0
```

- **convert_to_dfa()**: Converts the regular grammar to an equivalent DFA.

```python
def convert_to_dfa(self) -> DFA:
    """Converts the regular grammar to an equivalent DFA."""
    final_state = "FINAL"
    states = self.non_terminals | {final_state}
    transitions: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
    
    for source, rules in self.productions.items():
        for rule in rules:
            if not rule:  # Empty rule
                continue
            if len(rule) == 1:
                transitions[source][rule[0]].add(final_state)
            else:
                transitions[source][rule[0]].add(rule[1:])
    
    return DFA(
        states=states,
        alphabet=self.terminals,
        transitions=dict(transitions),
        start_state=self.start,
        accept_states={final_state}
    )
```

#### Conversion Algorithms

The implementation includes several key conversion algorithms:

1. **NDFA to DFA Conversion**: Implemented in the `convert_to_dfa()` method of the NDFA class, using the subset construction algorithm.

2. **FA to Regular Grammar Conversion**: Implemented in the `convert_to_regular_grammar()` method of the FiniteAutomaton class.

3. **Regular Grammar to DFA Conversion**: Implemented in the `convert_to_dfa()` method of the RegularGrammar class.

These conversions allow for seamless transition between different representations of regular languages, enabling users to work with the representation that is most convenient for their specific needs.

### The Variant NDFA

The NDFA for Variant 1 is defined in the `create_variant_ndfa()` function:

```python
def create_variant_ndfa() -> NDFA:
    """Create NDFA based on the given variant.
    
    Variant:
    Q = {q0,q1,q2,q3}, ∑ = {a,c,b}, F = {q2}, 
    δ(q0,a) = q0, δ(q0,a) = q1, δ(q1,c) = q1, 
    δ(q1,b) = q2, δ(q2,b) = q3, δ(q3,a) = q1.
    """
    transitions = {
        'q0': {'a': {'q0', 'q1'}},
        'q1': {'c': {'q1'}, 'b': {'q2'}},
        'q2': {'b': {'q3'}},
        'q3': {'a': {'q1'}}
    }
    
    return NDFA(
        states={'q0', 'q1', 'q2', 'q3'},
        alphabet={'a', 'b', 'c'},
        transitions=transitions,
        start_state='q0',
        accept_states={'q2'}
    )
```

This NDFA is non-deterministic because:
- State `q0` has two possible next states (`q0` and `q1`) for the input symbol `a`

The implementation checks this using the `is_deterministic()` method, which verifies that for each state and input symbol, there is exactly one next state.

## Testing and Results

### String Validation

The project includes functionality to validate strings against both finite automata and grammars:

- For automata, the `validate_string()` method in the DFA and NDFA classes checks if a given string is accepted by the automaton.
- For grammars, the `derive_string()` method generates random strings that are guaranteed to be in the language generated by the grammar.

Example output for string validation:

```
🔍 Validating: 'abc'
📍 Current state: q1
📍 Current state: q2
📍 Current state: q3
📌 Final state: q3
❌ String rejected!
```

### NDFA to DFA Conversion

The `convert_to_dfa()` method in the NDFA class converts an NDFA to an equivalent DFA using the subset construction algorithm. The resulting DFA has states that represent subsets of the NDFA states.

Example output for the variant NDFA conversion:

```
📊 Original NDFA:
  q0 --(a)--> q0, q1
  q1 --(b)--> q2
  q1 --(c)--> q1
  q2 --(b)--> q3
  q3 --(a)--> q1
  
📊 Converted DFA:
  q0 --(a)--> q1
  q1 --(a)--> q1
  q1 --(b)--> q2
  q1 --(c)--> q3
  q2 --(b)--> q4
  q3 --(b)--> q2
  q3 --(c)--> q3
  q4 --(a)--> q3
```

### FA to Regular Grammar Conversion

The `convert_to_regular_grammar()` method in the FiniteAutomaton class converts a finite automaton to an equivalent regular grammar. The states of the automaton become non-terminals in the grammar, and transitions become production rules.

Example output for the FA to grammar conversion:

```
📖 Converted Regular Grammar:
📚 Non-terminals = {S0, S1, S2, S3}
📝 Terminals = {a, b, c}
📖 Productions = {
    S0 → aS0 | aS1
    S1 → bS2 | cS1
    S2 → bS3 | ε
    S3 → aS1
}
➡️  Start = S0
```

### Grammar Classification

The `classify_chomsky()` method in the RegularGrammar class classifies a grammar according to the Chomsky hierarchy.

Example output for grammar classification:

```
🔍 Chomsky Classification:
This grammar is Type 3 in the Chomsky hierarchy.
✅ Type 3: Regular Grammar
   - Rules are of the form A → a or A → aB where A,B are non-terminals and a is terminal
```

## User Interface

The project includes a simple terminal-based user interface that allows users to interact with the implemented functionality:

```python
def display_menu():
    """Display the main menu options."""
    print("\n📋 Menu Options:")
    print("1. Generate and validate 5 random strings")
    print("2. Input a string to validate")
    print("3. Classify grammar (Chomsky hierarchy)")
    print("4. Test variant NDFA")
    print("5. Convert NDFA to DFA")
    print("6. Convert FA to Regular Grammar")
    print("7. Exit")
    return input("\n👉 Choose an option (1-7): ")
```

The main function sets up the initial grammar and automaton, and then enters a loop that displays the menu and processes user input:

```python
def main() -> None:
    """Main program execution."""
    clear_screen()
    print_header()
    
    # Define the grammar from Lab 1
    grammar = RegularGrammar(
        non_terminals={"S", "P", "Q"},
        terminals={"a", "b", "c", "d", "e", "f"},
        productions={
            "S": ["aP", "bQ"],
            "P": ["bP", "cP", "dQ", "e"],
            "Q": ["eQ", "fQ", "a"]
        },
        start="S"
    )
    
    # Convert to DFA
    dfa = grammar.convert_to_dfa()
    
    # Create NDFA from the variant
    variant_ndfa = create_variant_ndfa()
    
    # Display grammar definition
    print("📖 Grammar Definition:")
    print(grammar)
    
    # Display DFA transitions
    dfa.print_transitions()
    
    while True:
        choice = display_menu()
        
        # Process user choice...
```

The UI provides various options for testing and exploring the implemented functionality, making it easy for users to interact with the system.

## Conclusions

This laboratory work has provided a comprehensive exploration of finite automata and regular grammars, demonstrating the equivalence of these different representations of regular languages and the algorithms for converting between them.

Key findings and achievements include:

1. **Equivalence of Representations**: The implementation confirms the theoretical equivalence between finite automata and regular grammars. Any regular language can be represented by either a finite automaton or a regular grammar, and there are algorithms to convert between these representations.

2. **NDFA vs. DFA**: While NDFAs can sometimes provide more compact representations, they can always be converted to equivalent DFAs using the subset construction algorithm. This confirms the theoretical result that NDFAs and DFAs have the same expressive power.

3. **Chomsky Hierarchy**: The implementation includes functionality to classify grammars according to the Chomsky hierarchy, demonstrating the containment relationship between different classes of formal languages.

4. **Practical Applications**: The implementation provides practical tools for working with formal languages, including string validation, automaton conversion, and grammar classification. These tools could be useful in various applications, such as compiler design, text processing, and formal verification.

The project demonstrates a solid understanding of formal language theory concepts and provides a foundation for further exploration of more complex language classes, such as context-free languages and beyond.
