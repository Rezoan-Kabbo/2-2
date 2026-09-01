/**
 * Department Office colleague.
 * Confirms that a student has completed all academic requirements.
 * It never talks to the Controller, DSW, or the Student directly -
 * everything goes through the mediator.
 */
public class DepartmentOffice extends Colleague {

    public DepartmentOffice(ResultMediator mediator) {
        super(mediator);
        mediator.registerDepartmentOffice(this);
    }

    public void confirmCompletion(String studentId) {
        System.out.println("[Department Office] Confirming academic requirements completed for " + studentId);
        mediator.submitDepartmentalConfirmation(studentId);
    }
}
