-- ─────────────────────────────────────────────
-- One-table budget flow schema  (PostgreSQL)
-- ─────────────────────────────────────────────

CREATE TABLE public.flow_edge (
    id           BIGSERIAL PRIMARY KEY,      -- surrogate key
    item         TEXT NOT NULL,              -- node label
    amount       NUMERIC(16,2) NOT NULL,     -- positive = income, negative = expense
    parent_id    BIGINT REFERENCES public.flow_edge(id) ON DELETE RESTRICT,
    fiscal_year  SMALLINT NOT NULL,
    direction    TEXT NOT NULL,              -- 'income' | 'expense'
    province     CHAR(2) DEFAULT 'NA',       -- optional: 'ON', 'BC', etc.
    created_at   TIMESTAMPTZ DEFAULT now()
);

-- 1. Make sure direction values stay in the allowed set.
ALTER TABLE public.flow_edge
    ADD CONSTRAINT chk_direction
    CHECK (direction IN ('income','expense'));

-- 2. Keep amount sign consistent with direction.
ALTER TABLE public.flow_edge
    ADD CONSTRAINT chk_amount_sign
    CHECK (
        (direction = 'income'  AND amount >= 0) OR
        (direction = 'expense' AND amount <= 0)
    );

-- 3. A root node must have no parent_id.
ALTER TABLE public.flow_edge
    ADD CONSTRAINT chk_root_has_no_parent
    CHECK (
        (parent_id IS NULL AND item IN ('Income','Expenses'))
        OR parent_id IS NOT NULL
    );

-- 4. Prevent cycles in the hierarchy (simple depth check).
--    Creates a function that rejects any insert causing a loop.
CREATE OR REPLACE FUNCTION public.fn_check_cycle() RETURNS trigger AS $$
DECLARE
    current BIGINT := NEW.parent_id;
BEGIN
    WHILE current IS NOT NULL LOOP
        IF current = NEW.id THEN
            RAISE EXCEPTION 'Cycle detected in flow_edge hierarchy';
        END IF;
        SELECT parent_id INTO current FROM public.flow_edge WHERE id = current;
    END LOOP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_cycle
    BEFORE INSERT OR UPDATE ON public.flow_edge
    FOR EACH ROW EXECUTE FUNCTION public.fn_check_cycle();

-- 5. Useful indexes
CREATE INDEX idx_flow_edge_year   ON public.flow_edge (fiscal_year);
CREATE INDEX idx_flow_edge_parent ON public.flow_edge (parent_id);
CREATE INDEX idx_flow_edge_dir_year ON public.flow_edge (direction, fiscal_year);

-- ─────────────────────────────
-- Seed two root rows (one-time)
-- ─────────────────────────────
INSERT INTO public.flow_edge (item, amount, fiscal_year, direction)
VALUES
  ('Income',   0, 2024, 'income'),   -- amount can be updated later
  ('Expenses', 0, 2024, 'expense');