# Task 2: BUET Final Result Publication System — Mediator Pattern

## Pattern identified
**Mediator Design Pattern.**

The Department Office, Controller of Examinations, DSW, and Student never
communicate with one another directly. Every request, confirmation, and
status update is routed through a single central object,
`ResultProcessingCoordinator` (the concrete Mediator), which also enforces
the required processing sequence and rejects any request that violates it.

## Files
- `ResultMediator.java` — Mediator interface.
- `ResultProcessingCoordinator.java` — Concrete mediator; holds all
  per-student processing state and sequencing rules.
- `Colleague.java` — Abstract base for all participants; holds a reference
  to the mediator only (never to other colleagues).
- `DepartmentOffice.java`, `ControllerOfExaminations.java`, `DSW.java`,
  `Student.java` — Concrete colleagues.
- `StudentRecord.java` — Internal per-student state tracked by the
  coordinator (confirmation / office order / testimonial / certificate
  flags).
- `Main.java` — Demo driver that runs the exact 7-step sequence required
  by the assignment.

## Enforced sequence
1. Departmental confirmation (Department Office → Coordinator)
2. Office order (Coordinator → Controller), requires step 1
3. Testimonial (Coordinator → DSW), requires step 2
4. Certificate & transcript (Coordinator → Controller), requires step 3

Any out-of-order request is rejected with a clear message instead of being
processed.

## Compile & run
```bash
cd src
javac *.java
java Main
```

## What the demo shows
1. An attempt to issue the office order before departmental confirmation → rejected.
2. Departmental confirmation submitted for two students (Rifat, Mahin).
3. An early attempt to issue the certificate/transcript before the office
   order and testimonial exist → rejected.
4. Office order issued for Rifat.
5. Testimonial issued for Rifat; the same attempt for Mahin (who has no
   office order yet) is rejected — showing per-student sequence enforcement.
6. Certificate and transcript issued for Rifat.
7. Final notifications and status displayed for both students.
