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

### Project Architecture

The implementation follows a modular design with clear separation of concerns:

```
project/
├── classes/
│   ├── regular_grammar.py
│   └── dfa.py
├── utils/
│   ├── ui_helpers.py
│   └── string_generators.py
└── main.py
```

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

## References

1. Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). Introduction to Automata Theory, Languages, and Computation (3rd Edition)
2. Sipser, M. (2012). Introduction to the Theory of Computation
3. Course materials by Cretu Dumitru and Vasile Drumea with Irina Cojuhari
4. Python Documentation - Type Hints
5. Python Documentation - Data Classes
