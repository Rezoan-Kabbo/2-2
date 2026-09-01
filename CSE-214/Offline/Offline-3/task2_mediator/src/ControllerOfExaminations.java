/**
 * Office of the Controller of Examinations colleague.
 * Issues the final-result office order (after departmental confirmation)
 * and later the certificate & transcript (after all prior steps).
 */
public class ControllerOfExaminations extends Colleague {

    public ControllerOfExaminations(ResultMediator mediator) {
        super(mediator);
        mediator.registerController(this);
    }

    public void issueOfficeOrder(String studentId) {
        System.out.println("[Controller of Examinations] Attempting to issue final-result office order for " + studentId);
        mediator.requestOfficeOrder(studentId);
    }

    public void issueCertificateAndTranscript(String studentId) {
        System.out.println("[Controller of Examinations] Attempting to issue certificate & transcript for " + studentId);
        mediator.requestCertificateAndTranscript(studentId);
    }
}
