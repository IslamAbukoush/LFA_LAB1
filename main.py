from typing import Set, Dict, List, Optional, Tuple
from dataclasses import dataclass
import random
from collections import defaultdict, deque
import time
import os

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print a stylized header."""
    print("=" * 60)
    print("🔤  FORMAL LANGUAGES LAB 1 & 2: AUTOMATA & GRAMMARS  🔤")
    print("=" * 60)
    print("\n👤 Name: Islam Abu koush")
    print("👥 Group: FAF-231")
    print("🔢 Variant: 1\n")
    print("=" * 60 + "\n")

def print_separator():
    """Print a separator line."""
    print("\n" + "-" * 60 + "\n")

@dataclass
class FiniteAutomaton:
    """Base class for Finite Automaton implementations."""
    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[str, Dict[str, Set[str]]]
    start_state: str
    accept_states: Set[str]
    
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
    
    def validate_string(self, input_str: str) -> bool:
        """Abstract method to validate a string."""
        raise NotImplementedError("Subclasses must implement this method")
    
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

class RegularGrammar:
    """Implementation of a Regular Grammar."""
    def __init__(self, non_terminals: Set[str], terminals: Set[str], 
                 productions: Dict[str, List[str]], start: str):
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self.start = start
        self._validate_grammar()
    
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
    
    def __str__(self) -> str:
        """Returns a formatted string representation of the grammar."""
        components = [
            f"📚 Non-terminals = {{{', '.join(sorted(self.non_terminals))}}}",
            f"📝 Terminals = {{{', '.join(sorted(self.terminals))}}}",
            "📖 Productions = {",
            *[f"    {left} → {' | '.join(sorted(right) if right else ['ε'])}"
              for left, right in self.productions.items()],
            "}",
            f"➡️  Start = {self.start}"
        ]
        return '\n'.join(components)

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
        
        if choice == "1":
            print("\n🎲 Generating and validating 5 random strings:")
            print_separator()
            for i in range(5):
                print(f"\n📝 String {i + 1}:")
                valid_string = grammar.derive_string()
                dfa.validate_string(valid_string)
                time.sleep(1)  # Add a small delay between validations
        
        elif choice == "2":
            print("\n⌨️  Enter a string to validate (using letters a-f):")
            user_input = input("👉 ").lower()
            dfa.validate_string(user_input)
        
        elif choice == "3":
            chomsky_type = grammar.classify_chomsky()
            print(f"\n🔍 Chomsky Classification:")
            print(f"This grammar is Type {chomsky_type} in the Chomsky hierarchy.")
            
            if chomsky_type == 3:
                print("✅ Type 3: Regular Grammar")
                print("   - Rules are of the form A → a or A → aB where A,B are non-terminals and a is terminal")
            elif chomsky_type == 2:
                print("✅ Type 2: Context-Free Grammar")
                print("   - Rules are of the form A → α where A is a non-terminal and α is a string of terminals and non-terminals")
            elif chomsky_type == 1:
                print("✅ Type 1: Context-Sensitive Grammar")
                print("   - Rules are of the form αAβ → αγβ where A is a non-terminal and α,β,γ are strings with |γ| ≥ 1")
            else:
                print("✅ Type 0: Unrestricted Grammar")
                print("   - No restrictions on production rules")
        
        elif choice == "4":
            print("\n🧪 Testing Variant NDFA:")
            print("\n📊 NDFA States: ", variant_ndfa.states)
            print("📊 NDFA Alphabet: ", variant_ndfa.alphabet)
            print("📊 NDFA Start State: ", variant_ndfa.start_state)
            print("📊 NDFA Accept States: ", variant_ndfa.accept_states)
            variant_ndfa.print_transitions()
            
            is_deterministic = variant_ndfa.is_deterministic()
            print(f"\n🔍 Is Deterministic: {'✅ Yes' if is_deterministic else '❌ No'}")
            
            if not is_deterministic:
                print("❓ Reason for non-determinism:")
                for state in variant_ndfa.states:
                    if state in variant_ndfa.transitions:
                        for symbol in variant_ndfa.alphabet:
                            if symbol in variant_ndfa.transitions[state]:
                                if len(variant_ndfa.transitions[state][symbol]) > 1:
                                    print(f"   - State {state} has multiple transitions for symbol {symbol}: {variant_ndfa.transitions[state][symbol]}")
            
            print("\n⌨️  Enter a string to validate (using letters a, b, c):")
            user_input = input("👉 ").lower()
            variant_ndfa.validate_string(user_input)
        
        elif choice == "5":
            print("\n🔄 Converting NDFA to DFA:")
            variant_dfa = variant_ndfa.convert_to_dfa()
            print("\n📊 Original NDFA:")
            variant_ndfa.print_transitions()
            print("\n📊 Converted DFA:")
            variant_dfa.print_transitions()
            print(f"📊 DFA States: {variant_dfa.states}")
            print(f"📊 DFA Start State: {variant_dfa.start_state}")
            print(f"📊 DFA Accept States: {variant_dfa.accept_states}")
            
            print("\n⌨️  Enter a string to validate with the converted DFA (using letters a, b, c):")
            user_input = input("👉 ").lower()
            variant_dfa.validate_string(user_input)
        
        elif choice == "6":
            print("\n🔄 Converting Finite Automaton to Regular Grammar:")
            fa_to_convert = variant_ndfa
            
            print("\n📊 Original FA:")
            fa_to_convert.print_transitions()
            
            converted_grammar = fa_to_convert.convert_to_regular_grammar()
            print("\n📖 Converted Regular Grammar:")
            print(converted_grammar)
            
            # Classify the converted grammar
            chomsky_type = converted_grammar.classify_chomsky()
            print(f"\n🔍 Chomsky Classification of Converted Grammar: Type {chomsky_type}")
            
            # Test the converted grammar
            print("\n🧪 Testing the converted grammar:")
            print("Generating a sample string...")
            try:
                sample_string = converted_grammar.derive_string()
                print(f"Generated string: {sample_string}")
            except Exception as e:
                print(f"Error generating string: {e}")
        
        elif choice == "7":
            print("\n👋 Thank you for using the Grammar & Automata Lab! Goodbye!")
            break
        
        else:
            print("\n❌ Invalid option. Please choose 1-7.")
        
        input("\n⏎  Press Enter to continue...")
        clear_screen()
        print_header()
        
        # Reset the display
        print("📖 Grammar Definition:")
        print(grammar)
        print("\n📊 DFA from Lab 1:")
        dfa.print_transitions()

if __name__ == "__main__":
    main()
