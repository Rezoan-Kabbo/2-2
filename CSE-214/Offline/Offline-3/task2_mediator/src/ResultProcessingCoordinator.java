import java.util.HashMap;
import java.util.Map;

/**
 * Concrete Mediator.
 *
 * Every request, confirmation, and status update between the Department
 * Office, the Controller of Examinations, DSW, and Students passes
 * through this single coordinator. None of the offices hold a reference
 * to one another - they only know about this mediator, which enforces
 * the required processing sequence:
 *
 *   1. Departmental confirmation
 *   2. Office order (Controller)
 *   3. Testimonial (DSW)
 *   4. Certificate & transcript (Controller)
 */
public class ResultProcessingCoordinator implements ResultMediator {

    private final Map<String, Student> students = new HashMap<>();
    private final Map<String, StudentRecord> records = new HashMap<>();

    private DepartmentOffice departmentOffice;
    private ControllerOfExaminations controller;
    private DSW dsw;

    @Override
    public void registerStudent(Student student) {
        students.put(student.getId(), student);
        records.put(student.getId(), new StudentRecord());
        System.out.println("[Coordinator] Registered student " + student.getName() + " (" + student.getId() + ")");
    }

    @Override
    public void registerDepartmentOffice(DepartmentOffice departmentOffice) {
        this.departmentOffice = departmentOffice;
        System.out.println("[Coordinator] Registered Department Office");
    }

    @Override
    public void registerController(ControllerOfExaminations controller) {
        this.controller = controller;
        System.out.println("[Coordinator] Registered Controller of Examinations");
    }

    @Override
    public void registerDSW(DSW dsw) {
        this.dsw = dsw;
        System.out.println("[Coordinator] Registered DSW");
    }

    @Override
    public void submitDepartmentalConfirmation(String studentId) {
        StudentRecord record = getRecord(studentId);
        record.departmentConfirmed = true;
        System.out.println("[Coordinator] Departmental confirmation recorded for " + studentId);
        notifyStudent(studentId, "Your departmental confirmation has been received.");
    }

    @Override
    public void requestOfficeOrder(String studentId) {
        StudentRecord record = getRecord(studentId);
        if (!record.departmentConfirmed) {
            System.out.println("[Coordinator] REJECTED: Cannot issue office order for " + studentId
                    + " - departmental confirmation is missing.");
            return;
        }
        record.officeOrderIssued = true;
        System.out.println("[Coordinator] Office order issued for " + studentId);
        notifyStudent(studentId, "Final-result office order has been issued.");
    }

    @Override
    public void requestTestimonial(String studentId) {
        StudentRecord record = getRecord(studentId);
        if (!record.officeOrderIssued) {
            System.out.println("[Coordinator] REJECTED: Cannot issue testimonial for " + studentId
                    + " - office order has not been issued yet.");
            return;
        }
        record.testimonialIssued = true;
        System.out.println("[Coordinator] Testimonial issued for " + studentId);
        notifyStudent(studentId, "Your testimonial has been issued.");
    }

    @Override
    public void requestCertificateAndTranscript(String studentId) {
        StudentRecord record = getRecord(studentId);
        if (!record.testimonialIssued) {
            System.out.println("[Coordinator] REJECTED: Cannot issue certificate & transcript for " + studentId
                    + " - required prior steps are not complete.");
            return;
        }
        record.certificateIssued = true;
        System.out.println("[Coordinator] Certificate and transcript issued for " + studentId);
        notifyStudent(studentId, "Your certificate and academic transcript have been issued.");
    }

    @Override
    public void notifyStudent(String studentId, String message) {
        Student student = students.get(studentId);
        if (student != null) {
            student.receiveNotification(message);
        }
    }

    @Override
    public String getStatus(String studentId) {
        return getRecord(studentId).toString();
    }

    private StudentRecord getRecord(String studentId) {
        StudentRecord record = records.get(studentId);
        if (record == null) {
            throw new IllegalArgumentException("Unknown student id: " + studentId);
        }
        return record;
    }
}
