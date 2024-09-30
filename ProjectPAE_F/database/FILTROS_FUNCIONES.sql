DROP PROCEDURE FuncionEstudiantesAction;
DROP PROCEDURE FuncionEstudiantesActionByDate;

-- ultima modificacion al filtrado por fecha agregandole el filtrado por grado de manera opcional para la busqueda de las acciones 
DELIMITER //

CREATE PROCEDURE FuncionEstudiantesActionByDate(
    IN action_date DATE,
    IN student_grade VARCHAR(50)
)
BEGIN
    -- Si el grado no se proporciona, lo asignamos a 'Todos'
    IF student_grade IS NULL THEN
        SET student_grade = 'Todos';
    END IF;

    IF student_grade = 'Todos' THEN
        -- Filtra solo por fecha si no se proporciona el grado o es 'Todos'
        SELECT Documento, Nombres, Apellidos, Grado, Action, ActionTime
        FROM EstudiantesActions
        WHERE DATE(ActionTime) = action_date
        ORDER BY Apellidos, Nombres;
    ELSE
        -- Filtra por fecha y grado
        SELECT Documento, Nombres, Apellidos, Grado, Action, ActionTime
        FROM EstudiantesActions
        WHERE DATE(ActionTime) = action_date AND Grado = student_grade
        ORDER BY Apellidos, Nombres;
    END IF;
END //

DELIMITER ;


-- funcion estudiante action con limite de acciones para evitar duplicados completo
DELIMITER //

CREATE PROCEDURE FuncionEstudiantesAction(IN est_id INT)
BEGIN
    DECLARE estudiante_nombres VARCHAR(100);
    DECLARE estudiante_apellidos VARCHAR(100);
    DECLARE estudiante_grado VARCHAR(50);
    DECLARE action_type VARCHAR(20);
    DECLARE current_count INT;

    -- Obtener los datos del estudiante
    SELECT Nombres, Apellidos, Grado 
    INTO estudiante_nombres, estudiante_apellidos, estudiante_grado
    FROM estudiantes 
    WHERE Documento = est_id;
    
    -- Determinar la acción basada en la hora actual
    IF CURRENT_TIME() BETWEEN '08:00:00' AND '10:00:00' THEN
        SET action_type = 'Refrigerio';
    ELSEIF CURRENT_TIME() BETWEEN '12:00:00' AND '22:40:00' THEN
        SET action_type = 'Almuerzo';
    ELSE
        -- Si está fuera del horario permitido, no hacer nada
        SET action_type = NULL;
    END IF;

    -- Solo proceder si la acción está dentro de los horarios permitidos
    IF action_type IS NOT NULL THEN
        -- Verificar si ya se ha registrado esta acción específica (Refrigerio o Almuerzo) hoy
        SELECT COUNT(*) INTO current_count
        FROM EstudiantesActions
        WHERE Documento = est_id 
        AND DATE(ActionTime) = CURDATE()
        AND Action = action_type;
        
        -- Solo insertar si esta acción no se ha registrado aún hoy
        IF current_count = 0 THEN
            INSERT INTO EstudiantesActions (Documento, Nombres, Apellidos, Grado, ActionTime, Action)
            VALUES (est_id, estudiante_nombres, estudiante_apellidos, estudiante_grado, NOW(), action_type);
        END IF;
    END IF;

    -- Devolver los datos del estudiante, ordenados por apellido
    SELECT Documento, Nombres, Apellidos, Grado, Action, ActionTime
    FROM EstudiantesActions
    WHERE Documento = est_id AND DATE(ActionTime) = CURDATE()
    ORDER BY Apellidos;
END //

DELIMITER ;



