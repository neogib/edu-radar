CREATE OR REPLACE FUNCTION public.szkola_set_geom_3857()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.geom IS NULL THEN
        NEW.geom_3857 := NULL;
    ELSE
        NEW.geom_3857 := ST_Transform(NEW.geom, 3857);
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_szkola_set_geom_3857 ON public.szkola;

CREATE TRIGGER trg_szkola_set_geom_3857
BEFORE INSERT OR UPDATE OF geom
ON public.szkola
FOR EACH ROW
EXECUTE FUNCTION public.szkola_set_geom_3857();
