package com.example.demo.students;

import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@CrossOrigin(origins = "*")
@RestController
@RequestMapping("/api/students")
public class StudentController {

    private final StudentRepository repo;

    public StudentController(StudentRepository repo) {
        this.repo = repo;
    }

    @GetMapping
    public List<Student> list() { return repo.findAll(); }

    @GetMapping("/{id}")
    public Student get(@PathVariable Long id) {
        return repo.findById(id).orElseThrow(() -> new StudentNotFound(id));
    }

    @GetMapping("/by-email")
    public Student byEmail(@RequestParam String email) {
        return repo.findByEmailIgnoreCase(email).orElseThrow(() -> new StudentNotFound(email));
    }

    @ResponseStatus(HttpStatus.CREATED)
    @PostMapping
    public Student create(@RequestBody Student body) {
        if (repo.existsByEmailIgnoreCase(body.getEmail())) throw new EmailTaken(body.getEmail());
        return repo.save(new Student(body.getName(), body.getEmail()));
    }

    @PutMapping("/{id}")
    public Student update(@PathVariable Long id, @RequestBody Student body) {
        Student s = repo.findById(id).orElseThrow(() -> new StudentNotFound(id));
        if (!s.getEmail().equalsIgnoreCase(body.getEmail()) && repo.existsByEmailIgnoreCase(body.getEmail()))
            throw new EmailTaken(body.getEmail());
        s.setName(body.getName());
        s.setEmail(body.getEmail());
        return repo.save(s);
    }

    @PatchMapping("/{id}")
    public Student patch(@PathVariable Long id, @RequestBody Map<String, String> body) {
        Student s = repo.findById(id).orElseThrow(() -> new StudentNotFound(id));
        if (body.containsKey("name")) s.setName(body.get("name"));
        if (body.containsKey("email")) {
            String newEmail = body.get("email");
            if (!s.getEmail().equalsIgnoreCase(newEmail) && repo.existsByEmailIgnoreCase(newEmail))
                throw new EmailTaken(newEmail);
            s.setEmail(newEmail);
        }
        return repo.save(s);
    }

    @ResponseStatus(HttpStatus.NO_CONTENT)
    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) {
        if (!repo.existsById(id)) throw new StudentNotFound(id);
        repo.deleteById(id);
    }

    @ResponseStatus(HttpStatus.CONFLICT)
    @ExceptionHandler(EmailTaken.class)
    public ErrorDTO handleEmailTaken(EmailTaken ex) { return new ErrorDTO("conflict", ex.getMessage()); }

    @ResponseStatus(HttpStatus.NOT_FOUND)
    @ExceptionHandler(StudentNotFound.class)
    public ErrorDTO handleNotFound(StudentNotFound ex) { return new ErrorDTO("not_found", ex.getMessage()); }

    @ResponseStatus(HttpStatus.CONFLICT)
    @ExceptionHandler(DataIntegrityViolationException.class)
    public ErrorDTO handleDiVe(DataIntegrityViolationException ex) { return new ErrorDTO("conflict", "Email ya existe."); }
}

class StudentNotFound extends RuntimeException {
    StudentNotFound(Object key) { super("Student no encontrado: " + key); }
}
class EmailTaken extends RuntimeException {
    EmailTaken(String email) { super("Email ya en uso: " + email); }
}
record ErrorDTO(String code, String message) {}
