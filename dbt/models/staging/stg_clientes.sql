{{ config(materialized='view', schema='staging') }}

WITH source AS (
    SELECT
        id,
        nombre,
        fecha_ingreso,
        valor_estimado,
        estado_funnel,
        -- Campos de control
        created_at,
        updated_at
    FROM {{ source('operational', 'clientes') }}
),

transformed AS (
    SELECT
        -- IDs y claves
        id as cliente_id,

        -- Campos normalizados
        UPPER(TRIM(nombre)) as nombre_cliente,
        LOWER(TRIM(nombre)) as nombre_cliente_lower,

        -- Fechas normalizadas
        CAST(fecha_ingreso AS DATE) as fecha_ingreso,
        CAST(created_at AS TIMESTAMP) as fecha_creacion,
        CAST(updated_at AS TIMESTAMP) as fecha_actualizacion,

        -- Valores numéricos con validación
        CASE
            WHEN valor_estimado >= 0 THEN valor_estimado
            ELSE NULL
        END as valor_estimado,

        -- Estados normalizados
        CASE
            WHEN estado_funnel IN ('Prospecto', 'Contactado', 'Calificado', 'Propuesta', 'Negociación', 'Ganado', 'Perdido')
                THEN estado_funnel
            ELSE 'Desconocido'
        END as estado_funnel,

        -- Campos calculados
        DATE_DIFF('day', CAST(fecha_ingreso AS DATE), CURRENT_DATE) as dias_desde_ingreso,

        -- Metadatos de transformación
        CURRENT_TIMESTAMP as _etl_loaded_at,
        '{{ invocation_id }}' as _dbt_job_id

    FROM source
)

SELECT * FROM transformed
