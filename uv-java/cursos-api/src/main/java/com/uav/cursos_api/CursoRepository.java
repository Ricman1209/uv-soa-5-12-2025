package com.uav.cursos_api;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface CursoRepository extends JpaRepository<Curso, Integer> {

    // Buscar por nombre exacto
    List<Curso> findByNombre(String nombre);

    // Eliminar por nombre
    @Transactional
    @Modifying
    @Query("DELETE FROM Curso c WHERE c.nombre = :nombre")
    int deleteByNombre(@Param("nombre") String nombre);

    // Buscar por fecha
    @Query("SELECT c FROM Curso c WHERE DATE(c.fechaCreacion) = DATE(:fecha)")
    List<Curso> findByFechaCreacion(@Param("fecha") LocalDateTime fecha);

    // Eliminar por fecha
    @Transactional
    @Modifying
    @Query("DELETE FROM Curso c WHERE DATE(c.fechaCreacion) = DATE(:fecha)")
    int deleteByFechaCreacion(@Param("fecha") LocalDateTime fecha);
}