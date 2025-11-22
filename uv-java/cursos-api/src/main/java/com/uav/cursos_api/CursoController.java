package com.uav.cursos_api;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/cursos") // http://localhost:8080/api/cursos
public class CursoController {

    @Autowired
    private CursoRepository repositorio;

    // 1. Obtener todos los cursos (GET)
    @GetMapping
    public List<Curso> obtenerTodos() {
        return repositorio.findAll();
    }

    // 2. Crear un nuevo curso (POST)
    @PostMapping
    public Curso guardarCurso(@RequestBody Curso nuevoCurso) {
        return repositorio.save(nuevoCurso);
    }
}