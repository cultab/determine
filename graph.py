"""Convert a non Deterministic Finite State Automaton read from a file to a Deterministic one.

Written with python version 3.9.1 although older version should work fine (3.7+ should be just fine).
"""

from itertools import chain, combinations, product


def main():
    """Load, convert, save and export some NDAs."""
    Nfa = FiniteStateAuto.from_file("./Nfa.txt")  # load example file
    Nfa.save_to_dot("Nfa.gv")  # export for rendering

    Dfa = translate_to_deterministic(Nfa)  # determine
    Dfa.save_to_dot("Dfa.gv")  # export for rendering
    Dfa.save_to_file("Dfa.txt")  # save to file

    Nfa2 = FiniteStateAuto.from_file("./Nfa2.txt")
    Nfa2.save_to_dot("Nfa2.gv")

    Dfa2 = translate_to_deterministic(Nfa2)
    Dfa2.save_to_dot("Dfa2.gv")  # export with names as is
    Dfa2.normalize_state_names()
    Dfa2.save_to_file("Dfa2.txt")

    Nfa3 = FiniteStateAuto.from_file("./Nfa3.txt")
    Nfa3.save_to_dot("Nfa3.gv")

    Dfa3 = translate_to_deterministic(Nfa3)
    Dfa3.normalize_state_names()  # export after normalizing
    Dfa3.save_to_dot("Dfa3.gv")
    Dfa3.save_to_file("Dfa3.txt")

    # dear god...
    Nfa4 = FiniteStateAuto.from_file("./Nfa4.txt")
    Nfa4.save_to_dot("Nfa4.gv")

    Dfa4 = translate_to_deterministic(Nfa4)
    Dfa4.save_to_dot("Dfa4.gv")
    Dfa4.normalize_state_names()  # export after normalizing
    Dfa4.save_to_file("Dfa4.txt")


class State(str):
    """Represents a state.

    It's just a string with 2 special constructors
    and a helpful constant: null
    """

    null = "∅"

    @staticmethod
    def from_number(n):
        """Create a State from anything that can be converted to an integer.

        Must be non-negative

        Examples:
        >>> State.fromNumber(5)
        >>> 'q1'
        >>> State.fromNumber('12')
        >>> 'q12'
        """
        try:
            if (num := int(n)) >= 0:
                return f"q{num}"
        except ValueError:
            raise TypeError("Number given must be convertible to int.")

    @staticmethod
    def from_set(state_set):
        """Create a state from a set of states.

        Examples:
        >>> State.from_set(['q1','q2'])
        >>> 'q1q2'
        >>> State.from_set(['q0','q3','q5'])
        >>> 'q0q3q5'
        """
        return "".join(state_set)


class FiniteStateAuto:
    """Represents a Finite State Automaton."""

    def __init__(self, count, alphabet, start, end, transitions, states=None):
        """Instantiate a new FiniteStateAuto.

        If it's not given a set of states, it creates them from the
        state count given.
        """
        self.alphabet = alphabet
        self.start_state = start
        self.end_states = end
        self.transitions = transitions
        # if not given state names, create them from the state count
        # assumes state names in transitions are increasing numbers
        if states is None:
            self.states = [State.from_number(state) for state in range(count)]
        else:
            self.states = states

    @property
    def state_count(self):
        """Calculate the state count dynamically.

        Examples:
        >>> Dfa.states
        >>> {'q0' 'q1'}
        >>> Dfa.state_count  # note no () at the end
        >>> 2
        """
        return len(self.states)

    @classmethod
    def from_file(cls, filename):
        """Create a FiniteStateAuto from a file."""
        with open(filename) as file:
            state_count = int(file.readline().strip())
            alphabet = file.readline().strip().split(" ")
            start_state = State.from_number(file.readline().strip())
            end_states = [
                State.from_number(end_state)
                for end_state in file.readline().strip().split(" ")
            ]

            transitions = list()
            for line in file:
                transition = line.strip().split(" ")
                transition[0] = State.from_number(transition[0])
                transition[2] = State.from_number(transition[2])
                transitions.append(transition)

        return cls(state_count, alphabet, start_state, end_states, transitions)

    @classmethod
    def empty(cls):
        """Return an empty FiniteStateAuto."""
        return cls(0, [], -1, [], [], states=[])

    def __repr__(self):
        """Return a pretty string representing the object."""
        trans_str_complete = ""
        for trans_str in [  # list comprehension magic
            f"\t[{trans[0]}\t--{trans[1]}-->\t{trans[2]}],\n"
            for trans in self.transitions
        ]:
            trans_str_complete += trans_str
        return (
            f"Number of states: {self.state_count}\n"
            f"Start state: {self.start_state}\n"
            f"End states: {self.end_states}\n"
            f"Alphabet: {self.alphabet}\n"
            f"Transitions: [\n{trans_str_complete}]\n"
            f"States: {self.states}\n"
        )

    def normalize_state_names(self):
        """Return a FiniteStateAuto with normalized state names.

        Normalized in this context means that states named after
        state sets and the null state are renamed.

        Example:
        >>> Dfa.states
        >>> {'q0', 'q1', 'q0q1', '∅'}
        >>> Dfa.normalize_state_names()
        >>> Dfa.states
        >>> {'q0', 'q1', 'q2', 'q3'}

        """
        name_map = {}  # maps old state names to new state names
        for state, new_name in zip(self.states, range(len(self.states))):
            name_map[state] = State.from_number(new_name)

        # rename states
        self.states = set([name_map[state] for state in self.states])
        # rename transitions
        self.transitions = [[name_map[trans[0]], trans[1], name_map[trans[2]]] for trans in self.transitions]
        # rename end states
        self.end_states = [name_map[end_state] for end_state in self.end_states]
        # rename start state
        self.start_state = name_map[self.start_state]

    def save_to_file(self, filename):
        """Save the FiniteStateAuto to a file.

        Although all 'q's in state names are removed
        and the null state is given a numerical name,
        it's a better idea to just normalize_state_names()
        before you save a FiniteStateAuto.
        """
        # with sys.stdout as file: used to debug
        null_name = f"{len(self.states) + 1}"  # number to write instead of '∅'
        with open(filename, "w") as file:
            file.write(f"{self.state_count}\n"
                       f"{' '.join(self.alphabet)}\n"
                       f"{self.start_state.replace('q', '').replace('∅', null_name)}\n"
                       f"{' '.join(self.end_states).replace('q', '').replace('∅', null_name)}\n")

            for transition in self.transitions:
                file.write(f"{' '.join(transition).replace('q', '').replace('∅', null_name)}\n")

    def save_to_dot(self, filename):
        """Save the FiniteStateAuto to a GraphViz file.

        Such a file can then be used to render the FiniteStateAuto
        into a png, pdf, etc.. like so

        ```sh
        $ dot <filename> -T<filetype> -o <output_filename>
        ```
        """
        with open(filename, "w") as file:
            file.write(
                "digraph G {\n"
                "rankdir=\"LR\"\n"
                "\tnode [shape=circle style=filled fillcolor=yellow fixedsize=true width=1.1 height=1.1]\n"
                "\tstart [shape=plaintext, fillcolor=none]\n"
            )
            if "∅" in self.states:
                file.write("\t∅ [fillcolor=darksalmon fontsize=20]\n")
            for end_state in self.end_states:
                file.write(f"\t{end_state} [shape=doublecircle]\n")

            file.write(f"\tstart -> {self.start_state};\n")
            for trans in self.transitions:
                file.write(f'\t{trans[0]} -> {trans[2]} [label="{trans[1]}"];\n')

            file.write("}")


def translate_to_deterministic(Nfa):
    """Convert a non-deterministic FiniteStateAuto to a deterministic one.

    Returns a deterministic FiniteStateAuto
    """
    # Deterministic finite (state) automation
    Dfa = FiniteStateAuto.empty()

    # copy attributes that stay the same
    Dfa.start_state = Nfa.start_state
    Dfa.alphabet = Nfa.alphabet

    for state in powerset(Nfa.states):
        # at this point Dfa's states are sets of Nda's states so for each
        # Nda state(SUBSTATE) that's in a Dfa state, if the SUBSTATE is
        # an end_state of the Nda then the state is an end state of the Dfa

        if state:  # check for null state
            Dfa.states.append(State.from_set(state))
        else:
            Dfa.states.append(State.null)
        for substate in state:
            if substate in Nfa.end_states:
                Dfa.end_states.append(State.from_set(state))
                break

    # get transitions for every combination of symbol and state
    for state, symbol in product(Dfa.states, Dfa.alphabet):
        d_set = list()  # destination states that state can reach with symbol
        for trans in Nfa.transitions:
            if trans[0] in state and trans[1] == symbol:
                d_set.append(trans[2])
        if d_set:  # if d_set contains states
            d_set = list(set(d_set))  # filter duplicates
            d_set.sort()  # 'q0q2q1' -> 'q0q1q2'
            Dfa.transitions.append([state, symbol, State.from_set(d_set)])
        else:  # if state does not transition to any state, it transitions to null
            if state:
                Dfa.transitions.append([state, symbol, State.null])
            else:  # self loop from null to null
                Dfa.transitions.append([State.null, symbol, State.null])

    walked = set()

    def walk(state):
        """Recursively walk graph to find reachable states.

        Defined in a closure with a FiniteStateAuto named "Dfa"
        and a set named "walked"
        """
        if state in walked:  # if state has been reached before, return
            return
        for trans in Dfa.transitions:
            if trans[0] == state:  # walk the transitions that start from state
                walked.add(state)
                walk(trans[2])  # walk to the transition destination

    walk(Dfa.start_state)  # walk from the start

    # only keep reachable states
    Dfa.states = walked

    # remove transitions that reference unreachable states
    for transition in list(Dfa.transitions):  # explicitly make a copy to iterate over
        if transition[0] not in Dfa.states or transition[2] not in Dfa.states:
            Dfa.transitions.remove(transition)

    # remove end states that don't exist anymore
    for end_state in list(Dfa.end_states):
        if end_state not in Dfa.states:
            Dfa.end_states.remove(end_state)

    return Dfa


# adapted from https://docs.python.org/3/library/itertools.html#itertools-recipes
def powerset(iterable):
    """Return an iterator to the powerset of an iterable.

    Example:
    >>> powerset([1,2,3]) -> (,) (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)

    Note: the actual return value is an iterator that yields the above values
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt, exiting...")
        exit(0)
