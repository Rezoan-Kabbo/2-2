/**
 * Tracks the processing status of a single student's result-publication
 * pipeline. Used internally by the ResultProcessingCoordinator only.
 */
public class StudentRecord {

    boolean departmentConfirmed = false;
    boolean officeOrderIssued = false;
    boolean testimonialIssued = false;
    boolean certificateIssued = false;

    @Override
    public String toString() {
        if (certificateIssued) {
            return "COMPLETE - certificate and transcript issued";
        }
        if (testimonialIssued) {
            return "Testimonial issued - awaiting certificate & transcript";
        }
        if (officeOrderIssued) {
            return "Office order issued - awaiting testimonial";
        }
        if (departmentConfirmed) {
            return "Departmental confirmation received - awaiting office order";
        }
        return "Awaiting departmental confirmation";
    }
}
