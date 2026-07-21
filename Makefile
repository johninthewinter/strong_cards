.PHONY: verify verify-publication verify-red

verify:
	python3 -B scripts/verify.py
	python3 -B scripts/audit_publication.py

verify-publication:
	python3 -B scripts/audit_publication.py

verify-red:
	python3 -B scripts/verify_red_gates.py
