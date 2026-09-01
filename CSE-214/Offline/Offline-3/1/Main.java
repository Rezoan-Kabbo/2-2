import java.util.*;

// 1. Disaster Categories
enum DisasterCategory {
    EARTHQUAKE, FLOOD, FIRE
}

// 2. Alert Model Class
class Alert {
    private String title;
    private DisasterCategory category;
    private String location;
    private String severity;
    private String safetyInstructions;

    public Alert(String title, DisasterCategory category, String location, String severity, String safetyInstructions) {
        this.title = title;
        this.category = category;
        this.location = location;
        this.severity = severity;
        this.safetyInstructions = safetyInstructions;
    }

    public DisasterCategory getCategory() {
        return category;
    }

    public String getTitle() {
        return title;
    }

    @Override
    public String toString() {
        return String.format("[%s - %s] %s | Location: %s | Instructions: %s",
                severity, category, title, location, safetyInstructions);
    }
}

// 3. Observer Interface
interface CitizenObserver {
    void update(Alert alert);
}

// 4. Concrete Observer (Citizen)
class Citizen implements CitizenObserver {
    private String name;
    private List<Alert> receivedNotifications;

    public Citizen(String name) {
        this.name = name;
        this.receivedNotifications = new ArrayList<>();
    }

    public String getName() {
        return name;
    }

    @Override
    public void update(Alert alert) {
        receivedNotifications.add(alert);
        System.out.println("[ ALERT TO: " + name + "] " + alert.getTitle());
    }

    // Displays all notifications received by this specific citizen
    public void displayNotifications() {
        System.out.println("\n--- Notification Inbox for " + name + " ---");
        if (receivedNotifications.isEmpty()) {
            System.out.println("No alerts received.");
        } else {
            for (Alert alert : receivedNotifications) {
                System.out.println(alert);
            }
        }
        System.out.println("-----------------------------------");
    }
}

// 5. Subject Interface
interface AlertSubject {
    void registerCitizen(CitizenObserver citizen);
    void subscribe(CitizenObserver citizen, DisasterCategory category);
    void unsubscribe(CitizenObserver citizen, DisasterCategory category);
    void publishAlert(Alert alert);
}

// 6. Concrete Subject (BD Alert System)
class BDAlertSystem implements AlertSubject {
    private List<CitizenObserver> registeredCitizens;
    // Maps each category to a set of subscribed citizens to prevent duplicate subscriptions
    private Map<DisasterCategory, Set<CitizenObserver>> subscriptions;

    public BDAlertSystem() {
        registeredCitizens = new ArrayList<>();
        subscriptions = new EnumMap<>(DisasterCategory.class);
        for (DisasterCategory category : DisasterCategory.values()) {
            subscriptions.put(category, new HashSet<>());
        }
    }

    @Override
    public void registerCitizen(CitizenObserver citizen) {
        if (!registeredCitizens.contains(citizen)) {
            registeredCitizens.add(citizen);
            System.out.println("Registered new citizen: " + ((Citizen) citizen).getName());
        }
    }

    @Override
    public void subscribe(CitizenObserver citizen, DisasterCategory category) {
        if (registeredCitizens.contains(citizen)) {
            subscriptions.get(category).add(citizen);
            System.out.println(((Citizen) citizen).getName() + " subscribed to " + category + " alerts.");
        } else {
            System.out.println("Error: Citizen must be registered first.");
        }
    }

    @Override
    public void unsubscribe(CitizenObserver citizen, DisasterCategory category) {
        if (subscriptions.get(category).remove(citizen)) {
            System.out.println(((Citizen) citizen).getName() + " unsubscribed from " + category + " alerts.");
        }
    }

    @Override
    public void publishAlert(Alert alert) {
        System.out.println("\n>>> BD ALERT SYSTEM PUBLISHING: " + alert.getTitle() + " <<<");
        Set<CitizenObserver> subscribers = subscriptions.get(alert.getCategory());
        
        for (CitizenObserver citizen : subscribers) {
            citizen.update(alert);
        }
    }
}

// 7. Demonstration
public class Main {
    public static void main(String[] args) {
        BDAlertSystem system = new BDAlertSystem();

        // Create citizens
        Citizen alice = new Citizen("Alice");
        Citizen bob = new Citizen("Bob");
        Citizen charlie = new Citizen("Charlie");

        System.out.println("--- 1. Registering Citizens ---");
        system.registerCitizen(alice);
        system.registerCitizen(bob);
        system.registerCitizen(charlie);

        System.out.println("\n--- 2. Subscribing Citizens ---");
        system.subscribe(alice, DisasterCategory.EARTHQUAKE);
        system.subscribe(alice, DisasterCategory.FIRE);
        
        system.subscribe(bob, DisasterCategory.FLOOD);
        
        system.subscribe(charlie, DisasterCategory.EARTHQUAKE);
        system.subscribe(charlie, DisasterCategory.FLOOD);
        system.subscribe(charlie, DisasterCategory.FIRE);

        System.out.println("\n--- 3. Publishing Initial Alerts ---");
        system.publishAlert(new Alert(
                "Magnitude 6.5 Earthquake", 
                DisasterCategory.EARTHQUAKE, 
                "Sylhet", 
                "CRITICAL", 
                "Drop, cover, and hold on."
        ));

        system.publishAlert(new Alert(
                "Flash Flood Warning", 
                DisasterCategory.FLOOD, 
                "Sunamganj", 
                "HIGH", 
                "Move to higher ground immediately."
        ));

        system.publishAlert(new Alert(
                "Industrial Fire Breakout", 
                DisasterCategory.FIRE, 
                "Gazipur", 
                "SEVERE", 
                "Evacuate the area and avoid inhaling smoke."
        ));

        System.out.println("\n--- 4. Updating Subscriptions ---");
        // Bob realizes he also needs Earthquake alerts but no longer needs Flood alerts
        system.subscribe(bob, DisasterCategory.EARTHQUAKE);
        system.unsubscribe(bob, DisasterCategory.FLOOD);

        System.out.println("\n--- 5. Verifying Subscription Updates ---");
        // Publishing another flood alert (Bob should NOT receive this)
        system.publishAlert(new Alert(
                "Rising River Levels", 
                DisasterCategory.FLOOD, 
                "Kurigram", 
                "MODERATE", 
                "Prepare for possible evacuation."
        ));

        // Publishing another earthquake alert (Bob SHOULD receive this)
        system.publishAlert(new Alert(
                "Minor Aftershock", 
                DisasterCategory.EARTHQUAKE, 
                "Sylhet", 
                "LOW", 
                "Stay vigilant."
        ));

        System.out.println("\n--- 6. Displaying Final Notification Inboxes ---");
        alice.displayNotifications();
        bob.displayNotifications();
        charlie.displayNotifications();
    }
}

// To Run : javac *.java  java Main