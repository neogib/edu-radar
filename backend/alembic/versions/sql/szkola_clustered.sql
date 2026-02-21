CREATE OR REPLACE FUNCTION public.szkola_clustered(
    z integer,
    x integer,
    y integer,
    query_params json DEFAULT '{}'::json
)
RETURNS bytea
LANGUAGE sql
STABLE
STRICT
PARALLEL SAFE
AS $$
WITH tile_base AS (
    SELECT
        ST_TileEnvelope(z, x, y) AS env_3857
),
tile AS (
    SELECT
        tb.env_3857,
        ST_Expand(
            tb.env_3857,
            (ST_XMax(tb.env_3857) - ST_XMin(tb.env_3857)) * 0.1
        ) AS env_3857_buffered,
        CASE
            WHEN z >= 13 THEN NULL::double precision
            WHEN z <= 5 THEN (ST_XMax(tb.env_3857) - ST_XMin(tb.env_3857)) / 5.0
            WHEN z <= 6 THEN (ST_XMax(tb.env_3857) - ST_XMin(tb.env_3857)) / 6.0
            WHEN z <= 8 THEN (ST_XMax(tb.env_3857) - ST_XMin(tb.env_3857)) / 8.0
            WHEN z <= 10 THEN (ST_XMax(tb.env_3857) - ST_XMin(tb.env_3857)) / 12.0
            WHEN z <= 11 THEN (ST_XMax(tb.env_3857) - ST_XMin(tb.env_3857)) / 16.0
            ELSE (ST_XMax(tb.env_3857) - ST_XMin(tb.env_3857)) / 20.0
        END AS cell_size
    FROM tile_base AS tb
),
fp AS (
    SELECT
        string_to_array(NULLIF(query_params->>'type', ''), ',')::integer[] AS type_ids,
        string_to_array(NULLIF(query_params->>'status', ''), ',')::integer[] AS status_ids,
        string_to_array(NULLIF(query_params->>'category', ''), ',')::integer[] AS category_ids,
        string_to_array(NULLIF(query_params->>'career', ''), ',')::integer[] AS career_ids,
        NULLIF(query_params->>'minScore', '')::double precision AS min_score,
        NULLIF(query_params->>'maxScore', '')::double precision AS max_score,
        NULLIF(BTRIM(query_params->>'q'), '') AS search_query
),
source AS (
    SELECT
        s.id,
        s.nazwa,
        s.wynik,
        s.typ_id,
        s.status_publicznoprawny_id,
        s.geom_3857
    FROM public.szkola AS s
    CROSS JOIN tile AS t
    CROSS JOIN fp
    WHERE s.geom_3857 IS NOT NULL
      AND s.aktualna = true
      AND s.zlikwidowana = false
      AND s.geom_3857 && t.env_3857_buffered
      AND (
          fp.type_ids IS NULL
          OR s.typ_id = ANY(fp.type_ids)
      )
      AND (
          fp.status_ids IS NULL
          OR s.status_publicznoprawny_id = ANY(fp.status_ids)
      )
      AND (
          fp.category_ids IS NULL
          OR s.kategoria_uczniow_id = ANY(fp.category_ids)
      )
      AND (
          fp.career_ids IS NULL
          OR EXISTS (
              SELECT 1
              FROM public.szkolaksztalceniezawodowelink AS skl
              WHERE skl.szkola_id = s.id
                AND skl.ksztalcenie_zawodowe_id = ANY(fp.career_ids)
          )
      )
      AND (
          fp.min_score IS NULL
          OR s.wynik IS NULL
          OR s.wynik >= fp.min_score
      )
      AND (
          fp.max_score IS NULL
          OR s.wynik IS NULL
          OR s.wynik <= fp.max_score
      )
      AND (
          fp.search_query IS NULL
          OR s.nazwa ILIKE '%' || fp.search_query || '%'
          OR EXISTS (
              SELECT 1
              FROM public.miejscowosc AS m
              WHERE m.id = s.miejscowosc_id
                AND m.nazwa ILIKE '%' || fp.search_query || '%'
          )
      )
),
bucketed AS (
    SELECT
        s.id,
        s.wynik,
        s.geom_3857,
        (t.cell_size IS NULL) AS is_point,
        CASE
            WHEN t.cell_size IS NULL THEN s.id::bigint
            ELSE NULL::bigint
        END AS point_key,
        CASE
            WHEN t.cell_size IS NULL THEN NULL::bigint
            ELSE FLOOR(ST_X(s.geom_3857) / t.cell_size)::bigint
        END AS grid_x,
        CASE
            WHEN t.cell_size IS NULL THEN NULL::bigint
            ELSE FLOOR(ST_Y(s.geom_3857) / t.cell_size)::bigint
        END AS grid_y
    FROM source AS s
    CROSS JOIN tile AS t
),
aggregated AS (
    SELECT
        b.is_point,
        b.point_key,
        b.grid_x,
        b.grid_y,
        COUNT(*)::integer AS point_count,
        SUM(COALESCE(b.wynik, 0))::double precision AS sum_wynik,
        COUNT(b.wynik)::integer AS non_null_count,
        ST_Centroid(ST_Collect(b.geom_3857)) AS geom_3857,
        MIN(b.id)::integer AS first_id
    FROM bucketed AS b
    GROUP BY b.is_point, b.point_key, b.grid_x, b.grid_y
),
single_points AS (
    SELECT
        s.id,
        s.nazwa,
        s.wynik,
        ts.nazwa AS typ,
        sp.nazwa AS status
    FROM aggregated AS a
    JOIN source AS s ON s.id = a.first_id
    LEFT JOIN public.typ_szkoly AS ts ON ts.id = s.typ_id
    LEFT JOIN public.status_publicznoprawny AS sp ON sp.id = s.status_publicznoprawny_id
    WHERE a.point_count = 1
),
identified AS (
    SELECT
        a.*,
        CASE
            WHEN a.is_point THEN CONCAT('pt:', a.point_key::text)
            ELSE CONCAT('cl:', a.grid_x::text, ':', a.grid_y::text)
        END AS bucket_id,
        ABS(
            hashtext(
                CASE
                    WHEN a.is_point THEN CONCAT('pt:', a.point_key::text)
                    ELSE CONCAT('cl:', a.grid_x::text, ':', a.grid_y::text)
                END
            )::bigint
        ) AS hashed_bucket_id
    FROM aggregated AS a
),
prepared AS (
    SELECT
        ST_AsMVTGeom(i.geom_3857, t.env_3857, 4096, 64, true) AS geom,
        (i.point_count > 1) AS cluster,
        i.point_count,
        i.point_count AS point_count_abbreviated,
        i.sum_wynik AS sum,
        i.non_null_count AS "nonNullCount",
        CASE
            WHEN i.point_count = 1 THEN i.first_id
            ELSE NULL
        END AS id,
        CASE
            WHEN i.point_count = 1 THEN sp.nazwa
            ELSE NULL
        END AS nazwa,
        CASE
            WHEN i.point_count = 1 THEN sp.typ
            ELSE NULL
        END AS typ,
        CASE
            WHEN i.point_count = 1 THEN sp.status
            ELSE NULL
        END AS status,
        CASE
            WHEN i.point_count = 1 THEN sp.wynik
            ELSE NULL
        END AS wynik,
        CASE
            WHEN i.point_count = 1 THEN i.first_id::bigint
            ELSE -i.hashed_bucket_id
        END AS state_id,
        CASE
            WHEN i.point_count > 1 THEN i.hashed_bucket_id
            ELSE NULL
        END AS cluster_id,
        CASE
            WHEN i.point_count = 1 THEN i.first_id::bigint
            ELSE i.hashed_bucket_id + 3000000000::bigint
        END AS feature_id
    FROM identified AS i
    CROSS JOIN tile AS t
    LEFT JOIN single_points AS sp ON i.point_count = 1 AND sp.id = i.first_id
)
SELECT ST_AsMVT(prepared, 'szkola_clustered', 4096, 'geom', 'feature_id')
FROM prepared
WHERE geom IS NOT NULL;
$$;
