{{ config(materialized='view', schema='staging') }}

WITH source AS (
    SELECT
        id,
        numero_factura,
        cliente_id,
        fecha_emision,
        fecha_vencimiento,
        estado,
        monto_subtotal,
        monto_impuestos,
        monto_descuento,
        monto_total,
        monto_pagado,
        created_at,
        updated_at
    FROM {{ source('operational', 'facturas') }}
),

transformed AS (
    SELECT
        -- IDs y claves
        id as factura_id,
        numero_factura,
        cliente_id,

        -- Fechas normalizadas con validación
        CAST(fecha_emision AS DATE) as fecha_emision,
        CAST(fecha_vencimiento AS DATE) as fecha_vencimiento,
        CAST(created_at AS TIMESTAMP) as fecha_creacion,
        CAST(updated_at AS TIMESTAMP) as fecha_actualizacion,

        -- Estados normalizados
        CASE
            WHEN estado IN ('Borrador', 'Emitida', 'Pagada', 'Vencida', 'Cancelada')
                THEN estado
            ELSE 'Desconocido'
        END as estado_factura,

        -- Valores monetarios con validación y cálculo
        CASE WHEN monto_subtotal >= 0 THEN monto_subtotal ELSE 0 END as monto_subtotal,
        CASE WHEN monto_impuestos >= 0 THEN monto_impuestos ELSE 0 END as monto_impuestos,
        CASE WHEN monto_descuento >= 0 THEN monto_descuento ELSE 0 END as monto_descuento,
        CASE WHEN monto_total >= 0 THEN monto_total ELSE 0 END as monto_total,
        CASE WHEN monto_pagado >= 0 THEN monto_pagado ELSE 0 END as monto_pagado,

        -- Cálculos automáticos
        (monto_total - COALESCE(monto_pagado, 0)) as saldo_pendiente,
        CASE
            WHEN monto_total > 0 THEN ROUND(monto_pagado / monto_total * 100, 2)
            ELSE 0
        END as porcentaje_pagado,

        -- Indicadores calculados
        CASE WHEN CAST(fecha_vencimiento AS DATE) < CURRENT_DATE AND estado != 'Pagada'
             THEN TRUE ELSE FALSE END as esta_vencida,

        DATE_DIFF('day', CAST(fecha_vencimiento AS DATE), CURRENT_DATE) as dias_vencimiento,

        -- Metadatos
        CURRENT_TIMESTAMP as _etl_loaded_at,
        '{{ invocation_id }}' as _dbt_job_id

    FROM source
)

SELECT * FROM transformed
