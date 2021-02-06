fmt="pdf"
ext="pdf"

all: run render

check: run render show

run:
	python graph.py

render:
	dot Nfa.gv   -T${fmt} -o   Nfa.${ext}
	dot Dfa.gv   -T${fmt} -o   Dfa.${ext}
	dot Nfa2.gv  -T${fmt} -o  Nfa2.${ext}
	dot Dfa2.gv  -T${fmt} -o  Dfa2.${ext}
	dot Nfa3.gv  -T${fmt} -o  Nfa3.${ext}
	dot Dfa3.gv  -T${fmt} -o  Dfa3.${ext}


show:
	sxiv Nfa.png Dfa.png Nfa2.png Dfa2.png Nfa3.png Dfa3.png
