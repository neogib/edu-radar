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
WITH tile AS (
    SELECT
        ST_TileEnvelope(z, x, y) AS env_3857,
        ST_Transform(ST_TileEnvelope(z, x, y), 4326) AS env_4326,
        ST_Transform(
            ST_Expand(
                ST_TileEnvelope(z, x, y),
                (ST_XMax(ST_TileEnvelope(z, x, y)) - ST_XMin(ST_TileEnvelope(z, x, y))) * 0.1
            ),
            4326
        ) AS env_4326_buffered,
        CASE
            WHEN z >= 13 THEN NULL::double precision
            WHEN z <= 5 THEN (ST_XMax(ST_TileEnvelope(z, x, y)) - ST_XMin(ST_TileEnvelope(z, x, y))) / 5.0
            WHEN z <= 6 THEN (ST_XMax(ST_TileEnvelope(z, x, y)) - ST_XMin(ST_TileEnvelope(z, x, y))) / 6.0
            WHEN z <= 8 THEN (ST_XMax(ST_TileEnvelope(z, x, y)) - ST_XMin(ST_TileEnvelope(z, x, y))) / 8.0
            WHEN z <= 10 THEN (ST_XMax(ST_TileEnvelope(z, x, y)) - ST_XMin(ST_TileEnvelope(z, x, y))) / 12.0
            WHEN z <= 11 THEN (ST_XMax(ST_TileEnvelope(z, x, y)) - ST_XMin(ST_TileEnvelope(z, x, y))) / 16.0
            ELSE (ST_XMax(ST_TileEnvelope(z, x, y)) - ST_XMin(ST_TileEnvelope(z, x, y))) / 20.0
        END AS cell_size
),
filter_params AS (
    SELECT
        string_to_array(NULLIF(query_params->>'type', ''), ',')::integer[] AS type_ids,
        string_to_array(NULLIF(query_params->>'status', ''), ',')::integer[] AS status_ids,
        string_to_array(NULLIF(query_params->>'category', ''), ',')::integer[] AS category_ids,
        string_to_array(NULLIF(query_params->>'career', ''), ',')::integer[] AS career_ids,
        NULLIF(query_params->>'min_score', '')::double precision AS min_score,
        NULLIF(query_params->>'max_score', '')::double precision AS max_score,
        NULLIF(BTRIM(query_params->>'q'), '') AS search_query
),
source_points AS (
    SELECT
        s.id,
        s.nazwa,
        s.wynik,
        ts.nazwa AS typ,
        sp.nazwa AS status,
        ST_Transform(ST_CurveToLine(s.geom), 3857) AS geom_3857
    FROM public.szkola AS s
    LEFT JOIN public.typ_szkoly AS ts ON ts.id = s.typ_id
    LEFT JOIN public.status_publicznoprawny AS sp ON sp.id = s.status_publicznoprawny_id
    LEFT JOIN public.miejscowosc AS m ON m.id = s.miejscowosc_id
    CROSS JOIN tile AS t
    CROSS JOIN filter_params AS fp
    WHERE s.geom IS NOT NULL
      AND s.aktualna = true
      AND s.zlikwidowana = false
      AND s.geom && t.env_4326_buffered
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
          OR m.nazwa ILIKE '%' || fp.search_query || '%'
      )
),
bucketed AS (
    SELECT
        CASE
            WHEN t.cell_size IS NULL THEN CONCAT('pt:', sp.id::text)
            ELSE CONCAT(
                'cl:',
                FLOOR(ST_X(sp.geom_3857) / t.cell_size)::bigint::text,
                ':',
                FLOOR(ST_Y(sp.geom_3857) / t.cell_size)::bigint::text
            )
        END AS bucket_id,
        sp.id,
        sp.nazwa,
        sp.typ,
        sp.status,
        sp.wynik,
        sp.geom_3857
    FROM source_points AS sp
    CROSS JOIN tile AS t
),
aggregated AS (
    SELECT
        b.bucket_id,
        COUNT(*)::integer AS point_count,
        SUM(COALESCE(b.wynik, 0))::double precision AS sum_wynik,
        COUNT(b.wynik)::integer AS non_null_count,
        ST_Centroid(ST_Collect(b.geom_3857)) AS geom_3857,
        MIN(b.id)::integer AS first_id,
        MIN(b.nazwa) AS first_nazwa,
        MIN(b.typ) AS first_typ,
        MIN(b.status) AS first_status,
        MIN(b.wynik)::double precision AS first_wynik
    FROM bucketed AS b
    GROUP BY b.bucket_id
),
prepared AS (
    SELECT
        ST_AsMVTGeom(a.geom_3857, t.env_3857, 4096, 64, true) AS geom,
        (a.point_count > 1) AS cluster,
        a.point_count,
        a.point_count AS point_count_abbreviated,
        a.sum_wynik AS sum,
        a.non_null_count AS "nonNullCount",
        CASE
            WHEN a.point_count = 1 THEN a.first_id
            ELSE NULL
        END AS id,
        CASE
            WHEN a.point_count = 1 THEN a.first_nazwa
            ELSE NULL
        END AS nazwa,
        CASE
            WHEN a.point_count = 1 THEN a.first_typ
            ELSE NULL
        END AS typ,
        CASE
            WHEN a.point_count = 1 THEN a.first_status
            ELSE NULL
        END AS status,
        CASE
            WHEN a.point_count = 1 THEN a.first_wynik
            ELSE NULL
        END AS wynik,
        CASE
            WHEN a.point_count = 1 THEN a.first_id
            ELSE -ABS(hashtext(a.bucket_id))
        END AS state_id,
        CASE
            WHEN a.point_count > 1 THEN ABS(hashtext(a.bucket_id))
            ELSE NULL
        END AS cluster_id
    FROM aggregated AS a
    CROSS JOIN tile AS t
)
SELECT ST_AsMVT(prepared, 'szkola_clustered', 4096, 'geom')
FROM prepared
WHERE geom IS NOT NULL;
$$;
