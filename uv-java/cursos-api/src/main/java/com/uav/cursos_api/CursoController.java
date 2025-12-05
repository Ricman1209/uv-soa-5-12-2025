package com.uav.cursos_api;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/cursos")
@CrossOrigin(origins = "*")
public class CursoController {

    @Autowired
    private CursoRepository repositorio;

    // GET - Todos los cursos
    @GetMapping
    public List<Curso> obtenerTodos() {
        return repositorio.findAll();
    }

    // GET - Curso por ID
    @GetMapping("/{id}")
    public ResponseEntity<?> obtenerPorId(@PathVariable Integer id) {
        Optional<Curso> curso = repositorio.findById(id);
        if (curso.isPresent()) {
            return ResponseEntity.ok(curso.get());
        }
        Map<String, Object> r = new HashMap<>();
        r.put("exito", false);
        r.put("mensaje", "No se encontró curso con ID: " + id);
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(r);
    }

    // POST - Registrar curso
    @PostMapping
    public ResponseEntity<?> guardarCurso(@RequestBody Curso nuevoCurso) {
        Map<String, Object> r = new HashMap<>();
        try {
            Curso guardado = repositorio.save(nuevoCurso);
            r.put("exito", true);
            r.put("mensaje", "Curso registrado correctamente");
            r.put("curso", guardado);
            return ResponseEntity.status(HttpStatus.CREATED).body(r);
        } catch (Exception e) {
            r.put("exito", false);
            r.put("mensaje", "Error: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(r);
        }
    }

    // DELETE - Por ID
    @DeleteMapping("/{id}")
    public ResponseEntity<?> eliminarPorId(@PathVariable Integer id) {
        Map<String, Object> r = new HashMap<>();
        Optional<Curso> curso = repositorio.findById(id);
        if (curso.isPresent()) {
            repositorio.deleteById(id);
            r.put("exito", true);
            r.put("mensaje", "Curso '" + curso.get().getNombre() + "' eliminado");
            return ResponseEntity.ok(r);
        }
        r.put("exito", false);
        r.put("mensaje", "No se encontró curso con ID: " + id);
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(r);
    }

    // DELETE - Por nombre
    @DeleteMapping("/nombre/{nombre}")
    public ResponseEntity<?> eliminarPorNombre(@PathVariable String nombre) {
        Map<String, Object> r = new HashMap<>();
        String nombreDec = nombre.replace("%20", " ");
        List<Curso> cursos = repositorio.findByNombre(nombreDec);
        if (!cursos.isEmpty()) {
            int eliminados = repositorio.deleteByNombre(nombreDec);
            r.put("exito", true);
            r.put("mensaje", "Se eliminaron " + eliminados + " curso(s) con nombre: '" + nombreDec + "'");
            return ResponseEntity.ok(r);
        }
        r.put("exito", false);
        r.put("mensaje", "No se encontraron cursos con nombre: '" + nombreDec + "'");
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(r);
    }

    // DELETE - Por fecha (yyyy-MM-dd)
    @DeleteMapping("/fecha/{fecha}")
    public ResponseEntity<?> eliminarPorFecha(@PathVariable String fecha) {
        Map<String, Object> r = new HashMap<>();
        try {
            LocalDate ld = LocalDate.parse(fecha, DateTimeFormatter.ISO_LOCAL_DATE);
            LocalDateTime ldt = ld.atStartOfDay();
            List<Curso> cursos = repositorio.findByFechaCreacion(ldt);
            if (!cursos.isEmpty()) {
                int eliminados = repositorio.deleteByFechaCreacion(ldt);
                r.put("exito", true);
                r.put("mensaje", "Se eliminaron " + eliminados + " curso(s) de fecha: " + fecha);
                return ResponseEntity.ok(r);
            }
            r.put("exito", false);
            r.put("mensaje", "No hay cursos en fecha: " + fecha);
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(r);
        } catch (Exception e) {
            r.put("exito", false);
            r.put("mensaje", "Formato inválido. Use: yyyy-MM-dd");
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(r);
        }
    }

    // Health check
    @GetMapping("/health")
    public ResponseEntity<?> health() {
        Map<String, Object> r = new HashMap<>();
        r.put("status", "ok");
        r.put("service", "Cursos REST API");
        return ResponseEntity.ok(r);
    }
}