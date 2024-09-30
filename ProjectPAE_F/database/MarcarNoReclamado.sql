DROP PROCEDURE MarcarNoReclamado;

-- Funcion para marcar no reclamado segun la ausencia de los datos en la tabla action
DELIMITER //

CREATE PROCEDURE MarcarNoReclamado(IN action_date DATE)
BEGIN
    DECLARE est_id INT;
    DECLARE estudiante_nombres VARCHAR(100);
    DECLARE estudiante_apellidos VARCHAR(100);
    DECLARE estudiante_grado VARCHAR(50);
    DECLARE action_time DATETIME;
    DECLARE done INT DEFAULT 0;

    -- Cursor para recorrer todos los estudiantes
    DECLARE cur CURSOR FOR 
        SELECT Documento, Nombres, Apellidos, Grado 
        FROM estudiantes;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;

    -- Procesar cada estudiante
    read_loop: LOOP
        FETCH cur INTO est_id, estudiante_nombres, estudiante_apellidos, estudiante_grado;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Verificar si el estudiante realizó la acción de Refrigerio en el horario de 08:00 - 10:00
        SET action_time = CONCAT(action_date, ' 09:00:00');
        IF (SELECT COUNT(*) FROM EstudiantesActions 
            WHERE Documento = est_id AND DATE(ActionTime) = action_date 
            AND Action = 'Refrigerio') = 0 
            AND (SELECT COUNT(*) FROM EstudiantesActions 
                 WHERE Documento = est_id AND DATE(ActionTime) = action_date 
                 AND Action = 'No reclamó refrigerio') = 0 THEN
            -- Si no realizó la acción de Refrigerio y no hay un registro "No reclamo", insertar
            INSERT INTO EstudiantesActions (Documento, Nombres, Apellidos, Grado, ActionTime, Action)
            VALUES (est_id, estudiante_nombres, estudiante_apellidos, estudiante_grado, action_time, 'No reclamo Refrigerio');
        END IF;

        -- Verificar si el estudiante realizó la acción de Almuerzo en el horario de 12:00 - 13:40
        SET action_time = CONCAT(action_date, ' 13:00:00');
        IF (SELECT COUNT(*) FROM EstudiantesActions 
            WHERE Documento = est_id AND DATE(ActionTime) = action_date 
            AND Action = 'Almuerzo') = 0 
            AND (SELECT COUNT(*) FROM EstudiantesActions 
                 WHERE Documento = est_id AND DATE(ActionTime) = action_date 
                 AND Action = 'No reclamó almuerzo') = 0 THEN
            -- Si no realizó la acción de Almuerzo y no hay un registro "No reclamo", insertar
            INSERT INTO EstudiantesActions (Documento, Nombres, Apellidos, Grado, ActionTime, Action)
            VALUES (est_id, estudiante_nombres, estudiante_apellidos, estudiante_grado, action_time, 'No reclamo Almuerzo');
        END IF;

    END LOOP;

    CLOSE cur;
END //

DELIMITER ;






