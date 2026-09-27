-- Lex I Bare-Metal Immutability Triggers
CREATE TRIGGER IF NOT EXISTS prevent_lex_i_update
BEFORE UPDATE ON ash_strata
BEGIN
    SELECT RAISE(FAIL, 'LEX I VIOLATION: Updates to historical Ash Archive strata are strictly forbidden.');
END;

CREATE TRIGGER IF NOT EXISTS prevent_lex_i_delete
BEFORE DELETE ON ash_strata
BEGIN
    SELECT RAISE(FAIL, 'LEX I VIOLATION: Deletions from historical Ash Archive strata are strictly forbidden.');
END;
