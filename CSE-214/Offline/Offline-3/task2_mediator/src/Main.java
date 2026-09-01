/**
 * Demonstration of the BUET Final Result Publication System
 * implemented using the Mediator design pattern.
 *
 * Pattern used: MEDIATOR
 * The ResultProcessingCoordinator centralizes all communication between
 * DepartmentOffice, ControllerOfExaminations, DSW, and Student, so that
 * no office ever calls or controls another office directly.
 */
public class Main {

    public static void main(String[] args) {

        ResultMediator coordinator = new ResultProcessingCoordinator();

        DepartmentOffice departmentOffice = new DepartmentOffice(coordinator);
        ControllerOfExaminations controller = new ControllerOfExaminations(coordinator);
        DSW dsw = new DSW(coordinator);

        Student rifat = new Student(coordinator, "S1", "Rifat");
        Student mahin = new Student(coordinator, "S2", "Mahin");

        System.out.println("\n=== Step 1: Attempt to publish result BEFORE departmental confirmation ===");
        controller.issueOfficeOrder("S1");

        System.out.println("\n=== Step 2: Submission of departmental confirmation ===");
        departmentOffice.confirmCompletion("S1");
        departmentOffice.confirmCompletion("S2");

        System.out.println("\n=== Step 3: Early attempt to issue certificate/transcript (before office order & testimonial) ===");
        controller.issueCertificateAndTranscript("S1");

        System.out.println("\n=== Step 4: Issuance of the final-result office order ===");
        controller.issueOfficeOrder("S1");
        // S2's confirmation exists, but we intentionally skip S2's office order for now
        // to show that S2's later steps will also be correctly rejected.

        System.out.println("\n=== Step 5: Issuance of the testimonial ===");
        dsw.issueTestimonial("S1");
        System.out.println("--- Trying testimonial for S2 (no office order yet) ---");
        dsw.issueTestimonial("S2");

        System.out.println("\n=== Step 6: Issuance of the certificate and transcript ===");
        controller.issueCertificateAndTranscript("S1");

        System.out.println("\n=== Step 7: Student notifications and final status ===");
        rifat.displayNotifications();
        rifat.displayStatus();
        System.out.println();
        mahin.displayNotifications();
        mahin.displayStatus();
    }
}
