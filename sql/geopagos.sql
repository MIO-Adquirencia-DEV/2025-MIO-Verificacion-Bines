SELECT
    t.Numero_tarjeta AS [Numero tarjeta]
FROM Transaction_Retention_Daily T
         LEFT JOIN DBO.TEMPBIN TB ON TB.BIN = LEFT(T.Numero_tarjeta, 6)
WHERE TB.TipoProducto IS NULL
    AND t.Numero_tarjeta IS NOT NULL

