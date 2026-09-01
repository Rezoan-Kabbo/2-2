import java.util.ArrayList;
import java.util.List;

/**
 * Student colleague.
 * Receives notifications from the mediator whenever a processing step
 * concerning them is completed (or rejected), and can display the
 * notifications it has collected as well as its current status.
 */
public class Student extends Colleague {

    private final String id;
    private final String name;
    private final List<String> notifications = new ArrayList<>();

    public Student(ResultMediator mediator, String id, String name) {
        super(mediator);
        this.id = id;
        this.name = name;
        mediator.registerStudent(this);
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public void receiveNotification(String message) {
        notifications.add(message);
        System.out.println("    -> Notification to " + name + ": " + message);
    }

    public void displayNotifications() {
        System.out.println("Notifications received by " + name + " (" + id + "):");
        if (notifications.isEmpty()) {
            System.out.println("  (none)");
            return;
        }
        int i = 1;
        for (String note : notifications) {
            System.out.println("  " + (i++) + ". " + note);
        }
    }

    public void displayStatus() {
        System.out.println(name + "'s current status: " + mediator.getStatus(id));
    }
}
