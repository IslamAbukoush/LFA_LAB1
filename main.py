from typing import Set, Dict, List, Optional
from dataclasses import dataclass
import random
from collections import defaultdict
import time
import os

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print a stylized header."""
    print("=" * 60)
    print("🔤  FORMAL LANGUAGES LAB 1: REGULAR GRAMMARS & DFAs  🔤")
    print("=" * 60)
    print("\n👤 Name: Islam Abu koush")
    print("👥 Group: FAF-231")
    print("🔢 Variant: 1\n")
    print("=" * 60 + "\n")

def print_separator():
    """Print a separator line."""
    print("\n" + "-" * 60 + "\n")

@dataclass
class DFA:
    """Deterministic Finite Automaton implementation."""
    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[str, Dict[str, Set[str]]]
    start_state: str
    accept_states: Set[str]
    
    def validate_string(self, input_str: str) -> bool:
        """Validates whether an input string is accepted by the DFA."""
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

    def print_transitions(self) -> None:
        """Prints a formatted transition table."""
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
                assert rule[0] in self.terminals, f"First symbol in {rule} must be terminal"
                if len(rule) > 1:
                    assert rule[1] in self.non_terminals, f"Second symbol in {rule} must be non-terminal"
    
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
    
    def __str__(self) -> str:
        """Returns a formatted string representation of the grammar."""
        components = [
            f"📚 Non-terminals = {{{', '.join(sorted(self.non_terminals))}}}",
            f"📝 Terminals = {{{', '.join(sorted(self.terminals))}}}",
            "📖 Productions = {",
            *[f"    {left} → {' | '.join(sorted(right))}"
              for left, right in self.productions.items()],
            "}",
            f"➡️  Start = {self.start}"
        ]
        return '\n'.join(components)

def generate_test_string(alphabet: Set[str], min_len: int = 3, max_len: int = 10) -> str:
    """Generates a random test string from the given alphabet."""
    length = random.randint(min_len, max_len)
    return ''.join(random.choice(list(alphabet)) for _ in range(length))

def display_menu():
    """Display the main menu options."""
    print("\n📋 Menu Options:")
    print("1. Generate and validate 5 random strings")
    print("2. Input a string to validate")
    print("3. Exit")
    return input("\n👉 Choose an option (1-3): ")

def main() -> None:
    """Main program execution."""
    clear_screen()
    print_header()
    
    # Define the grammar
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
    
    # Display grammar definition
    print("📖 Grammar Definition:")
    print(grammar)
    
    # Convert to DFA and display transitions
    dfa = grammar.convert_to_dfa()
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
            print("\n👋 Thank you for using the Grammar Validator! Goodbye!")
            break
        
        else:
            print("\n❌ Invalid option. Please choose 1, 2, or 3.")
        
        input("\n⏎  Press Enter to continue...")
        clear_screen()
        print_header()
        print("📖 Grammar Definition:")
        print(grammar)
        dfa.print_transitions()

if __name__ == "__main__":
    main()