import os
import math
import json
from typing import Union, Optional, Set, Dict, List
from dataclasses import dataclass
import webbrowser

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

@dataclass
class DFA(FiniteAutomaton):
    """Deterministic Finite Automaton implementation."""
    pass

@dataclass
class NDFA(FiniteAutomaton):
    """Non-Deterministic Finite Automaton implementation."""
    
    def convert_to_dfa(self) -> DFA:
        """Converts the NDFA to an equivalent DFA using the subset construction algorithm."""
        from collections import deque
        
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
    
    def convert_to_dfa(self) -> DFA:
        """Converts the regular grammar to an equivalent DFA."""
        from collections import defaultdict
        
        final_state = "FINAL"
        states = self.non_terminals | {final_state}
        transitions = defaultdict(lambda: defaultdict(set))
        
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

def export_automaton_to_canvas(automaton, output_file: Optional[str] = None):
    """
    Export automaton to a Canvas JSON format for web visualization.
    
    Args:
        automaton: The FiniteAutomaton instance (DFA or NDFA)
        output_file: Optional filename to save the JSON output
    """
    nodes = []
    edges = []
    node_positions = {}
    
    # Calculate positions for nodes in a circle
    num_states = len(automaton.states)
    radius = 150
    center_x, center_y = 0, 0
    
    # Assign positions to states
    for i, state in enumerate(sorted(automaton.states)):
        angle = 2 * math.pi * i / num_states
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        node_positions[state] = (x, y)
        
        # Create node
        node_id = f"node_{state}"
        shape_style = {
            "fillColor": "#ffffcc" if state in automaton.accept_states else "#ffffff",
            "strokeColor": "#000000",
            "strokeWidth": 2,
            "cornerRadius": 10,
            "textSize": 12
        }
        
        if state in automaton.accept_states:
            # Double circle for accept states
            nodes.append({
                "id": f"{node_id}_outer",
                "type": "shape",
                "shape": "rectangle",
                "x": x - 30,
                "y": y - 30,
                "width": 60,
                "height": 60,
                "edges": [],
                "style": {
                    "fillColor": "transparent",
                    "strokeColor": "#000000",
                    "strokeWidth": 2,
                    "cornerRadius": 30
                }
            })
        
        nodes.append({
            "id": node_id,
            "type": "text",
            "text": state,
            "x": x - 20,
            "y": y - 10,
            "width": 40,
            "height": 20,
            "edges": [],
            "style": shape_style
        })
    
    # Add start state indicator
    start_x, start_y = node_positions[automaton.start_state]
    start_node_id = f"node_{automaton.start_state}"
    
    # Create start arrow
    start_arrow_id = "start_arrow"
    nodes.append({
        "id": start_arrow_id,
        "type": "text",
        "text": "start",
        "x": start_x - 100,
        "y": start_y - 10,
        "width": 40,
        "height": 20,
        "edges": [],
        "style": {"textSize": 12}
    })
    
    # Add the start edge
    edges.append({
        "id": f"edge_start",
        "from": {
            "type": "connected",
            "node": start_arrow_id,
            "side": "right"
        },
        "to": {
            "type": "connected",
            "node": f"node_{automaton.start_state}",
            "side": "left"
        },
        "style": {
            "strokeColor": "#000000",
            "strokeWidth": 2,
            "toEndStyle": 1  # Arrow
        }
    })
    
    # Add transitions
    for state in sorted(automaton.states):
        if state not in automaton.transitions:
            continue
        
        for symbol, targets in sorted(automaton.transitions[state].items()):
            for target in sorted(targets):
                # Create unique edge ID
                edge_id = f"edge_{state}_{symbol}_{target}"
                
                # Calculate appropriate sides for connection
                source_x, source_y = node_positions[state]
                target_x, target_y = node_positions[target]
                
                # Determine the best sides to connect based on relative positions
                dx = target_x - source_x
                dy = target_y - source_y
                
                source_side = "right" if dx > 0 else "left" if dx < 0 else "bottom" if dy > 0 else "top"
                target_side = "left" if dx > 0 else "right" if dx < 0 else "top" if dy > 0 else "bottom"
                
                # If it's a self-loop, use special positioning
                if state == target:
                    edges.append({
                        "id": edge_id,
                        "from": {
                            "type": "connected",
                            "node": f"node_{state}",
                            "side": "top"
                        },
                        "to": {
                            "type": "connected",
                            "node": f"node_{target}",
                            "side": "right"
                        },
                        "label": symbol,
                        "style": {
                            "strokeColor": "#000000",
                            "strokeWidth": 1,
                            "toEndStyle": 1  # Arrow
                        }
                    })
                else:
                    edges.append({
                        "id": edge_id,
                        "from": {
                            "type": "connected",
                            "node": f"node_{state}",
                            "side": source_side
                        },
                        "to": {
                            "type": "connected",
                            "node": f"node_{target}",
                            "side": target_side
                        },
                        "label": symbol,
                        "style": {
                            "strokeColor": "#000000",
                            "strokeWidth": 1,
                            "toEndStyle": 1  # Arrow
                        }
                    })
    
    # Create the canvas object
    canvas = {
        "nodes": nodes,
        "edges": edges
    }
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(canvas, f, indent=2)
        print(f"✅ Canvas JSON saved to {output_file}")
    
    return canvas

def create_svg_visualization(automaton, filename):
    """
    Create an SVG visualization of an automaton without requiring Graphviz.
    
    Args:
        automaton: The FiniteAutomaton instance
        filename: Output SVG filename
    """
    # Set up SVG dimensions
    width, height = 800, 600
    
    # Calculate node positions in a circle
    node_positions = {}
    num_states = len(automaton.states)
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 3
    
    for i, state in enumerate(sorted(automaton.states)):
        angle = 2 * math.pi * i / num_states
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        node_positions[state] = (x, y)
    
    # Start SVG content
    svg_content = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        '<defs>',
        '  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">',
        '    <polygon points="0 0, 10 3.5, 0 7" fill="#000" />',
        '  </marker>',
        '</defs>',
        '<rect width="100%" height="100%" fill="#f9f9f9" />',
        f'<text x="10" y="30" font-family="Arial" font-size="20" fill="#333">Automaton: {"DFA" if automaton.is_deterministic() else "NDFA"}</text>',
    ]
    
    # Group for transitions
    svg_content.append('<g id="transitions">')
    
    # Add transitions
    transitions_grouped = {}  # Group transitions by source and target
    
    for state in automaton.states:
        if state not in automaton.transitions:
            continue
            
        for symbol, targets in automaton.transitions[state].items():
            for target in targets:
                key = (state, target)
                if key in transitions_grouped:
                    transitions_grouped[key].append(symbol)
                else:
                    transitions_grouped[key] = [symbol]
    
    # Draw the transitions
    for (source, target), symbols in transitions_grouped.items():
        x1, y1 = node_positions[source]
        x2, y2 = node_positions[target]
        
        # Sort symbols for consistent output
        symbols.sort()
        label = ", ".join(symbols)
        
        if source == target:
            # Self-loop
            svg_content.append(f'  <path d="M {x1} {y1-20} C {x1-40} {y1-80}, {x1+40} {y1-80}, {x1} {y1-20}" ' +
                              f'stroke="#333" fill="none" stroke-width="1.5" marker-end="url(#arrowhead)" />')
            svg_content.append(f'  <text x="{x1}" y="{y1-60}" font-family="Arial" font-size="14" text-anchor="middle">{label}</text>')
        else:
            # Calculate position for the label
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            
            # Calculate control point for curved lines (to avoid overlapping)
            # More curved for closer nodes
            distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            curvature = max(50, 150 - distance/5)  # Less curvature for farther nodes
            
            # Normalize the perpendicular direction
            dx, dy = x2-x1, y2-y1
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                perpx, perpy = -dy/length, dx/length
            else:
                perpx, perpy = 0, 1
                
            # Control point
            ctrl_x = mid_x + perpx * curvature
            ctrl_y = mid_y + perpy * curvature
            
            # Label position (offset from control point toward middle)
            label_x = mid_x + perpx * (curvature * 0.7)
            label_y = mid_y + perpy * (curvature * 0.7) + 5  # +5 for text alignment
            
            # Draw curved line with control point
            svg_content.append(f'  <path d="M {x1} {y1} Q {ctrl_x} {ctrl_y}, {x2} {y2}" ' + 
                              f'stroke="#333" fill="none" stroke-width="1.5" marker-end="url(#arrowhead)" />')
            
            # Add the transition label
            svg_content.append(f'  <text x="{label_x}" y="{label_y}" font-family="Arial" font-size="14" ' +
                              f'text-anchor="middle" fill="#333">{label}</text>')
    
    svg_content.append('</g>')
    
    # Add start state arrow
    start_x, start_y = node_positions[automaton.start_state]
    svg_content.append('<g id="start-arrow">')
    svg_content.append(f'  <line x1="{start_x-70}" y1="{start_y}" x2="{start_x-30}" y2="{start_y}" ' +
                      f'stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)" />')
    svg_content.append(f'  <text x="{start_x-75}" y="{start_y-10}" font-family="Arial" font-size="14" ' +
                      f'text-anchor="end" fill="#333">start</text>')
    svg_content.append('</g>')
    
    # Add nodes
    svg_content.append('<g id="states">')
    
    for state in sorted(automaton.states):
        x, y = node_positions[state]
        
        # For accept states, draw double circle
        if state in automaton.accept_states:
            svg_content.append(f'  <circle cx="{x}" cy="{y}" r="25" fill="#ffffcc" stroke="#333" stroke-width="2" />')
            svg_content.append(f'  <circle cx="{x}" cy="{y}" r="20" fill="#ffffcc" stroke="#333" stroke-width="2" />')
        else:
            svg_content.append(f'  <circle cx="{x}" cy="{y}" r="20" fill="#fff" stroke="#333" stroke-width="2" />')
        
        # Add state label
        svg_content.append(f'  <text x="{x}" y="{y+5}" font-family="Arial" font-size="14" ' +
                         f'text-anchor="middle" fill="#333">{state}</text>')
    
    svg_content.append('</g>')
    
    # Add legend
    svg_content.append('<g id="legend" transform="translate(10, 40)">')
    svg_content.append('  <rect x="0" y="0" width="200" height="80" fill="#fff" stroke="#ccc" rx="5" ry="5" />')
    svg_content.append('  <text x="10" y="20" font-family="Arial" font-size="14" fill="#333">Legend:</text>')
    svg_content.append('  <circle cx="20" cy="40" r="10" fill="#fff" stroke="#333" stroke-width="2" />')
    svg_content.append('  <text x="40" y="45" font-family="Arial" font-size="12" fill="#333">Regular State</text>')
    svg_content.append('  <circle cx="20" cy="65" r="12" fill="#ffffcc" stroke="#333" stroke-width="2" />')
    svg_content.append('  <circle cx="20" cy="65" r="8" fill="#ffffcc" stroke="#333" stroke-width="2" />')
    svg_content.append('  <text x="40" y="70" font-family="Arial" font-size="12" fill="#333">Accept State</text>')
    svg_content.append('</g>')
    
    # Close SVG
    svg_content.append('</svg>')
    
    # Write to file
    with open(filename, 'w') as f:
        f.write('\n'.join(svg_content))
    
    print(f"✅ SVG visualization saved to {filename}")

def create_html_with_svgs():
    """Create an HTML file that includes all SVG visualizations."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Automata Visualization</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2 {
            text-align: center;
            color: #333;
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 40px;
        }
        .visualization {
            margin-top: 20px;
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 5px;
            background-color: #f9f9f9;
            width: 100%;
        }
        select {
            padding: 8px;
            margin: 10px 0;
            width: 300px;
            font-size: 16px;
        }
        .info {
            background-color: #e9f7fe;
            border: 1px solid #a6d8f5;
            padding: 15px;
            border-radius: 5px;
            margin: 20px auto;
            max-width: 800px;
        }
        .info h3 {
            margin-top: 0;
        }
        .tabs {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
        .tab {
            padding: 10px 20px;
            background-color: #ddd;
            border: 1px solid #ccc;
            border-bottom: none;
            border-radius: 5px 5px 0 0;
            cursor: pointer;
            margin: 0 5px;
        }
        .tab.active {
            background-color: #f9f9f9;
            border-bottom: 1px solid #f9f9f9;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        svg {
            max-width: 100%;
            height: auto;
        }
    </style>
</head>
<body>
    <h1>Automata Visualization</h1>
    
    <div class="info">
        <h3>About this Visualization</h3>
        <p>This page visualizes finite automata using SVG. Each tab shows a different automaton.</p>
        <p><strong>Instructions:</strong> Click on the tabs to switch between different automata.</p>
    </div>
    
    <div class="container">
        <div class="tabs">
            <div class="tab active" onclick="openTab('ndfa')">NDFA from Variant</div>
            <div class="tab" onclick="openTab('dfa')">DFA Converted from NDFA</div>
            <div class="tab" onclick="openTab('grammar')">DFA from Grammar</div>
        </div>
        
        <div class="visualization">
            <div id="ndfa" class="tab-content active">
                <h2>Non-Deterministic Finite Automaton (NDFA)</h2>
                <object data="variant_ndfa.svg" type="image/svg+xml" width="100%" height="600px">
                    Your browser does not support SVG
                </object>
            </div>
            <div id="dfa" class="tab-content">
                <h2>Deterministic Finite Automaton (DFA)</h2>
                <object data="variant_dfa.svg" type="image/svg+xml" width="100%" height="600px">
                    Your browser does not support SVG
                </object>
            </div>
            <div id="grammar" class="tab-content">
                <h2>DFA from Grammar</h2>
                <object data="grammar_dfa.svg" type="image/svg+xml" width="100%" height="600px">
                    Your browser does not support SVG
                </object>
            </div>
        </div>
    </div>
    
    <script>
        function openTab(tabName) {
            // Hide all tab content
            const tabContents = document.getElementsByClassName('tab-content');
            for (let i = 0; i < tabContents.length; i++) {
                tabContents[i].classList.remove('active');
            }
            
            // Remove active class from all tabs
            const tabs = document.getElementsByClassName('tab');
            for (let i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            
            // Show the selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to the clicked tab
            event.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
"""
    
    with open("automata_svg_viewer.html", "w") as f:
        f.write(html_content)
    
    print("✅ HTML viewer created: automata_svg_viewer.html")

def visualize_automata():
    """
    Main function to visualize automata.
    """
    # Print header
    print("=" * 60)
    print("🎨  AUTOMATA VISUALIZATION  🎨")
    print("=" * 60)
    
    # Create the NDFA from variant
    print("\n📊 Creating NDFA from variant 1...")
    variant_ndfa = create_variant_ndfa()
    
    # Create SVG visualization for NDFA
    print("\n📊 Creating SVG visualization for NDFA...")
    create_svg_visualization(variant_ndfa, "variant_ndfa.svg")
    
    # Convert NDFA to DFA
    print("\n🔄 Converting NDFA to DFA...")
    variant_dfa = variant_ndfa.convert_to_dfa()
    
    # Create SVG visualization for DFA
    print("\n📊 Creating SVG visualization for DFA...")
    create_svg_visualization(variant_dfa, "variant_dfa.svg")
    
    # Define the grammar from Lab 1
    print("\n📖 Creating Grammar from Lab 1...")
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
    
    # Convert grammar to DFA and visualize
    print("\n🔄 Converting Grammar to DFA...")
    grammar_dfa = grammar.convert_to_dfa()
    
    print("\n📊 Creating SVG visualization for Grammar DFA...")
    create_svg_visualization(grammar_dfa, "grammar_dfa.svg")
    
    # Export to canvas format for web visualization (optional)
    print("\n🌐 Exporting to web canvas format...")
    export_automaton_to_canvas(variant_ndfa, "variant_ndfa_canvas.json")
    export_automaton_to_canvas(variant_dfa, "variant_dfa_canvas.json")
    export_automaton_to_canvas(grammar_dfa, "grammar_dfa_canvas.json")
    
    # Create HTML viewer with SVGs
    print("\n📄 Creating HTML viewer with SVGs...")
    create_html_with_svgs()
    
    print("\n✅ All visualizations completed!")
    print("\nFiles created:")
    print("  - variant_ndfa.svg - SVG visualization of NDFA from your variant")
    print("  - variant_dfa.svg - SVG visualization of DFA converted from your variant NDFA")
    print("  - grammar_dfa.svg - SVG visualization of DFA converted from your grammar")
    print("  - automata_svg_viewer.html - HTML viewer for the SVG visualizations")
    
    # Try to open the HTML file in the browser
    try:
        print("\n🌐 Opening visualization in web browser...")
        webbrowser.open("automata_svg_viewer.html")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print("Please open automata_svg_viewer.html in your web browser manually.")

if __name__ == "__main__":
    visualize_automata()
