/**
 * Directorate of Students' Welfare (DSW) colleague.
 * Issues the testimonial, but only after the office order has been issued.
 */
public class DSW extends Colleague {

    public DSW(ResultMediator mediator) {
        super(mediator);
        mediator.registerDSW(this);
    }

    public void issueTestimonial(String studentId) {
        System.out.println("[DSW] Attempting to issue testimonial for " + studentId);
        mediator.requestTestimonial(studentId);
    }
}
