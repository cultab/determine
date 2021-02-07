fmt="pdf"
ext="pdf"

all: run render_graphs render_report

check: run render show

run:
	python graph.py

render_graphs:
	#
	dot Nfa.gv   -T${fmt} -o   Nfa.${ext}
	dot Dfa.gv   -T${fmt} -o   Dfa.${ext}
	#
	dot Nfa2.gv  -T${fmt} -o  Nfa2.${ext}
	dot Dfa2.gv  -T${fmt} -o  Dfa2.${ext}
	#
	dot Nfa3.gv  -T${fmt} -o  Nfa3.${ext}
	dot Dfa3.gv  -T${fmt} -o  Dfa3.${ext}
	#
	dot Nfa4.gv  -T${fmt} -o  Nfa4.${ext}
	dot Dfa4.gv  -T${fmt} -o  Dfa4.${ext}

render_report:
	R -e "require(rmarkdown);render('te.rmd');"


show:
	sxiv Nfa.png Dfa.png Nfa2.png Dfa2.png Nfa3.png Dfa3.png
