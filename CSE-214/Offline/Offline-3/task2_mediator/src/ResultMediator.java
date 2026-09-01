/**
 * Mediator interface for the BUET Final Result Publication System.
 * Declares the communication contract that all colleague offices use
 * to interact with each other indirectly, through the coordinator.
 */
public interface ResultMediator {

    void registerStudent(Student student);
    void registerDepartmentOffice(DepartmentOffice departmentOffice);
    void registerController(ControllerOfExaminations controller);
    void registerDSW(DSW dsw);

    void submitDepartmentalConfirmation(String studentId);
    void requestOfficeOrder(String studentId);
    void requestTestimonial(String studentId);
    void requestCertificateAndTranscript(String studentId);

    void notifyStudent(String studentId, String message);
    String getStatus(String studentId);
}
