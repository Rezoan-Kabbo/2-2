import java.util.*;

// ============================================================
//  No shared Behaviour. Each device is its own island.
//  Upgraded functionalities are booleans and fields crammed into each class.
//  Everything "works" but every new feature touches everything.
// ============================================================

class Light {
    boolean on = false;
    // Pro upgrade flags
    boolean accessRestricted = false;
    int pin = 0;
    boolean locked = false;
    boolean timerControlled = false;
    int timerSeconds = 0;
    boolean timerRunning = false;
    boolean powerThrottled = false;
    double powerCap = 0;

    void activate() {
        if (accessRestricted && locked) return;
        on = true;
        if (timerControlled) timerRunning = true;
    }

    void deactivate() {
        if (accessRestricted && locked) return;
        on = false;
        timerRunning = false;
    }

    double getPower() {
        double p = on ? 10.0 : 0.0;
        if (powerThrottled && p > powerCap) p = powerCap;
        return p;
    }

    String getStatus() {
        String s = "Light: " + (on ? "ON" : "OFF");
        if (accessRestricted && locked) s += " [LOCKED]";
        if (timerControlled && timerRunning) s += " (auto-off in " + timerSeconds + "s)";
        if (powerThrottled && on && 10.0 > powerCap) s += " [throttled to " + powerCap + "W]";
        return s;
    }
}

class Thermostat {
    boolean on = false;
    // Same flags copy-pasted from Light
    boolean accessRestricted = false;
    int pin = 0;
    boolean locked = false;
    boolean timerControlled = false;
    int timerSeconds = 0;
    boolean timerRunning = false;
    boolean powerThrottled = false;
    double powerCap = 0;

    void activate() {
        if (accessRestricted && locked) return;
        on = true;
        if (timerControlled) timerRunning = true;
    }

    void deactivate() {
        if (accessRestricted && locked) return;
        on = false;
        timerRunning = false;
    }

    double getPower() {
        double p = on ? 150.0 : 0.0;
        if (powerThrottled && p > powerCap) p = powerCap;
        return p;
    }

    String getStatus() {
        String s = "Thermostat: " + (on ? "ON" : "OFF");
        if (accessRestricted && locked) s += " [LOCKED]";
        if (timerControlled && timerRunning) s += " (auto-off in " + timerSeconds + "s)";
        if (powerThrottled && on && 150.0 > powerCap) s += " [throttled to " + powerCap + "W]";
        return s;
    }
}

class Speaker {
    boolean on = false;
    // Same flags AGAIN — copy-pasted a third time
    boolean accessRestricted = false;
    int pin = 0;
    boolean locked = false;
    boolean timerControlled = false;
    int timerSeconds = 0;
    boolean timerRunning = false;
    boolean powerThrottled = false;
    double powerCap = 0;

    void activate() {
        if (accessRestricted && locked) return;
        on = true;
        if (timerControlled) timerRunning = true;
    }

    void deactivate() {
        if (accessRestricted && locked) return;
        on = false;
        timerRunning = false;
    }

    double getPower() {
        double p = on ? 5.0 : 0.0;
        if (powerThrottled && p > powerCap) p = powerCap;
        return p;
    }

    String getStatus() {
        String s = "Speaker: " + (on ? "Playing" : "Idle");
        if (accessRestricted && locked) s += " [LOCKED]";
        if (timerControlled && timerRunning) s += " (auto-off in " + timerSeconds + "s)";
        if (powerThrottled && on && 5.0 > powerCap) s += " [throttled to " + powerCap + "W]";
        return s;
    }
}

// Rooms are basically a list of devices. But here, rooms can't just hold a list of "devices" — there's no shared type.
// So it holds three separate lists. Adding a fourth device type means
// editing Room, every helper method, and every demo.
class MessyRoom {
    String name;
    List<Light> lights = new ArrayList<>();
    List<Thermostat> thermostats = new ArrayList<>();
    List<Speaker> speakers = new ArrayList<>();
    // Track insertion order separately because three lists lost it
    List<Object> insertionOrder = new ArrayList<>();

    // Room-level enhancement flags
    boolean ecoMode = false;
    double ecoBudget = 0;
    boolean guestMode = false;
    Set<String> guestAllowed = new HashSet<>(); // "light", "thermostat", "speaker"

    MessyRoom(String name) { this.name = name; }

    void addLight(Light l) { lights.add(l); insertionOrder.add(l); }
    void addThermostat(Thermostat t) { thermostats.add(t); insertionOrder.add(t); }
    void addSpeaker(Speaker s) { speakers.add(s); insertionOrder.add(s); }

    void activateAll() {
        if (guestMode) {
            // Only activate allowed types
            if (guestAllowed.contains("light"))
                for (Light l : lights) l.activate();
            if (guestAllowed.contains("thermostat"))
                for (Thermostat t : thermostats) t.activate();
            if (guestAllowed.contains("speaker"))
                for (Speaker s : speakers) s.activate();
        } else {
            for (Light l : lights) l.activate();
            for (Thermostat t : thermostats) t.activate();
            for (Speaker s : speakers) s.activate();
        }

        // EcoMode: shed in reverse insertion order
        if (ecoMode && getTotalPower() > ecoBudget) {
            for (int i = insertionOrder.size() - 1; i >= 0 && getTotalPower() > ecoBudget; i--) {
                Object dev = insertionOrder.get(i);
                if (dev instanceof Light) {
                    ((Light) dev).deactivate();
                    System.out.println("    >> EcoMode: shed [" + ((Light) dev).getStatus() + "]");
                } else if (dev instanceof Thermostat) {
                    ((Thermostat) dev).deactivate();
                    System.out.println("    >> EcoMode: shed [" + ((Thermostat) dev).getStatus() + "]");
                } else if (dev instanceof Speaker) {
                    ((Speaker) dev).deactivate();
                    System.out.println("    >> EcoMode: shed [" + ((Speaker) dev).getStatus() + "]");
                }
                // Every new device type needs another else-if here
            }
        }
    }

    void deactivateAll() {
        for (Light l : lights) l.deactivate();
        for (Thermostat t : thermostats) t.deactivate();
        for (Speaker s : speakers) s.deactivate();
    }

    double getTotalPower() {
        double total = 0;
        if (guestMode) {
            if (guestAllowed.contains("light"))
                for (Light l : lights) total += l.getPower();
            if (guestAllowed.contains("thermostat"))
                for (Thermostat t : thermostats) total += t.getPower();
            if (guestAllowed.contains("speaker"))
                for (Speaker s : speakers) total += s.getPower();
        } else {
            for (Light l : lights) total += l.getPower();
            for (Thermostat t : thermostats) total += t.getPower();
            for (Speaker s : speakers) total += s.getPower();
        }
        if (ecoMode && total > ecoBudget) total = ecoBudget;
        return total;
    }

    String getStatus() {
        StringBuilder sb = new StringBuilder("[" + name + "]");
        if (ecoMode) sb.insert(0, "[ECO: " + ecoBudget + "W budget]\n");
        if (guestMode) sb.insert(0, "[GUEST MODE]\n");

        // Can't just loop "devices" — have to loop each list separately
        for (Object dev : insertionOrder) {
            if (dev instanceof Light) {
                Light l = (Light) dev;
                sb.append("\n  ").append(l.getStatus());
                if (guestMode && !guestAllowed.contains("light"))
                    sb.append(" [guest-restricted]");
            } else if (dev instanceof Thermostat) {
                Thermostat t = (Thermostat) dev;
                sb.append("\n  ").append(t.getStatus());
                if (guestMode && !guestAllowed.contains("thermostat"))
                    sb.append(" [guest-restricted]");
            } else if (dev instanceof Speaker) {
                Speaker s = (Speaker) dev;
                sb.append("\n  ").append(s.getStatus());
                if (guestMode && !guestAllowed.contains("speaker"))
                    sb.append(" [guest-restricted]");
            }
            // ANOTHER else-if for every new device type
        }
        return sb.toString();
    }
}

// Home is basically Room's logic copy-pasted with "rooms" instead of "devices"
class MessyHome {
    String name;
    List<MessyRoom> rooms = new ArrayList<>();
    // Home-level eco/guest — duplicated from Room
    boolean ecoMode = false;
    double ecoBudget = 0;
    boolean guestMode = false;
    Set<String> guestAllowed = new HashSet<>();

    MessyHome(String name) { this.name = name; }
    void addRoom(MessyRoom r) { rooms.add(r); }

    void activateAll() {
        for (MessyRoom r : rooms) r.activateAll();
        // Home-level eco — completely separate logic from Room-level eco
        if (ecoMode && getTotalPower() > ecoBudget) {
            // Shed entire rooms in reverse order... ugly
            for (int i = rooms.size() - 1; i >= 0 && getTotalPower() > ecoBudget; i--) {
                rooms.get(i).deactivateAll();
            }
        }
    }

    void deactivateAll() {
        for (MessyRoom r : rooms) r.deactivateAll();
    }

    double getTotalPower() {
        double total = 0;
        for (MessyRoom r : rooms) total += r.getTotalPower();
        if (ecoMode && total > ecoBudget) total = ecoBudget;
        return total;
    }

    String getStatus() {
        StringBuilder sb = new StringBuilder("=== " + name + " ===");
        if (ecoMode) sb.insert(0, "[ECO: " + ecoBudget + "W budget]\n");
        if (guestMode) sb.insert(0, "[GUEST MODE]\n");
        for (MessyRoom r : rooms) sb.append("\n").append(r.getStatus());
        return sb.toString();
    }
}

// ============================================================
//  MAIN — Some demos, but built on the mess above
// ============================================================

public class SmartHomeSpaghettiDemo {

    public static void main(String[] args) {
        demoA();
        demoB();
        demoC();
        demoD();
        demoE();
        demoF();
    }

    static void header(String title) {
        System.out.println("\n" + "=".repeat(55));
        System.out.println("  " + title);
        System.out.println("=".repeat(55));
    }

    // DEMO A: Home overview
    static void demoA() {
        header("DEMO A: Home Overview");

        MessyRoom living = new MessyRoom("Living Room");
        living.addLight(new Light());
        living.addSpeaker(new Speaker());

        MessyRoom bedroom = new MessyRoom("Bedroom");
        bedroom.addLight(new Light());
        bedroom.addThermostat(new Thermostat());

        MessyHome home = new MessyHome("My Home");
        home.addRoom(living);
        home.addRoom(bedroom);

        System.out.println("Before activation:");
        System.out.println(home.getStatus());
        System.out.println("Power: " + home.getTotalPower() + "W");

        home.activateAll();
        System.out.println("\nAfter activation:");
        System.out.println(home.getStatus());
        System.out.println("Power: " + home.getTotalPower() + "W");
    }

    // DEMO B: Stacking device-level "upgrades"
    static void demoB() {
        header("DEMO B: AccessRestricted + TimerControlled");

        Light light = new Light();
        // "Upgrading" = flipping flags. No composition, no wrapping.
        light.accessRestricted = true;
        light.pin = 1234;
        light.locked = true;
        light.timerControlled = true;
        light.timerSeconds = 60;

        System.out.println("Step 1 — Activate while locked:");
        light.activate();
        System.out.println("  Status: " + light.getStatus());
        System.out.println("  Power:  " + light.getPower() + "W");

        System.out.println("\nStep 2 — Wrong PIN:");
        // Unlock logic is here in main, not encapsulated anywhere
        if (0000 == light.pin) { light.locked = false; System.out.println("    >> Unlock SUCCESS"); }
        else { System.out.println("    >> Unlock FAILED"); }
        System.out.println("  Status: " + light.getStatus());

        System.out.println("\nStep 3 — Correct PIN, activate:");
        if (1234 == light.pin) { light.locked = false; System.out.println("    >> Unlock SUCCESS"); }
        else { System.out.println("    >> Unlock FAILED"); }
        light.activate();
        System.out.println("  Status: " + light.getStatus());
        System.out.println("  Power:  " + light.getPower() + "W");

        System.out.println("\nStep 4 — Timer expires:");
        // Simulating timer — manually calling deactivate because there's
        // no timer object, no dedicated class, just a flag
        if (light.timerRunning) {
            System.out.println("    >> Timer expired — auto-deactivating.");
            light.on = false;        // reaching directly into internals
            light.timerRunning = false;
        }
        System.out.println("  Status: " + light.getStatus());
        System.out.println("  Power:  " + light.getPower() + "W");
    }

    // DEMO C: EcoMode
    static void demoC() {
        header("DEMO C: EcoMode (budget = 100W)");

        MessyRoom office = new MessyRoom("Office");
        office.addLight(new Light());
        office.addLight(new Light());
        office.addThermostat(new Thermostat());
        office.ecoMode = true;
        office.ecoBudget = 100;

        System.out.println("Activating with EcoMode:");
        office.activateAll();
        System.out.println("\n" + office.getStatus());
        System.out.println("Power: " + office.getTotalPower() + "W");
    }

    // DEMO D: Order matters
    static void demoD() {
        header("DEMO D: Order Matters");

        // Setup 1: Throttled thermostat
        MessyRoom room1 = new MessyRoom("Lab-1");
        room1.addLight(new Light());
        room1.addLight(new Light());
        Thermostat t1 = new Thermostat();
        t1.powerThrottled = true;
        t1.powerCap = 80;
        room1.addThermostat(t1);
        room1.ecoMode = true;
        room1.ecoBudget = 100;

        System.out.println("Setup 1: Throttled thermostat (80W) + EcoMode(100W)");
        room1.activateAll();
        System.out.println(room1.getStatus());
        System.out.println("Power: " + room1.getTotalPower() + "W");

        // Setup 2: Raw thermostat
        MessyRoom room2 = new MessyRoom("Lab-2");
        room2.addLight(new Light());
        room2.addLight(new Light());
        room2.addThermostat(new Thermostat());
        room2.ecoMode = true;
        room2.ecoBudget = 100;

        System.out.println("\nSetup 2: Raw thermostat (150W) + EcoMode(100W)");
        room2.activateAll();
        System.out.println(room2.getStatus());
        System.out.println("Power: " + room2.getTotalPower() + "W");
    }

    // DEMO E: GuestMode
    static void demoE() {
        header("DEMO E: GuestMode + Mixed Enhancements");

        MessyRoom guest = new MessyRoom("Guest Room");

        guest.addSpeaker(new Speaker());

        Thermostat lockedThermo = new Thermostat();
        lockedThermo.accessRestricted = true;
        lockedThermo.pin = 9999;
        lockedThermo.locked = true;
        guest.addThermostat(lockedThermo);

        Light timedLight = new Light();
        timedLight.timerControlled = true;
        timedLight.timerSeconds = 120;
        guest.addLight(timedLight);

        guest.guestMode = true;
        guest.guestAllowed.add("light");
        guest.guestAllowed.add("speaker");

        System.out.println("Activating GuestMode room:");
        guest.activateAll();
        System.out.println("\n" + guest.getStatus());
        System.out.println("Guest-visible power: " + guest.getTotalPower() + "W");
    }

    // DEMO F: "Enhance an entire room"
    // THIS IS WHERE THE SPAGHETTI CODE STUGGLES MOST.
    // There's no way to upgrade a Room with AccessRestricted or TimerControlled
    // because those are boolean flags on device classes, not composable objects.
    // We have to fake it with MORE flags on the Room itself.
    static void demoF() {
        header("DEMO F: prepareForNight wraps a Room");

        MessyRoom kids = new MessyRoom("Kids Room");
        kids.addLight(new Light());
        kids.addSpeaker(new Speaker());
        kids.addThermostat(new Thermostat());

        // Can't call prepareForNight(kids) because Room and Light
        // are completely different .
        // So we add MORE flags to Room. Copy-paste from device logic.
        boolean roomLocked = true;
        int roomPin = 0;
        boolean roomTimerControlled = true;
        int roomTimerSeconds = 3600;
        boolean roomTimerRunning = false;

        System.out.println("Step 1 — Activate while locked (nothing happens):");
        if (!roomLocked) {
            kids.activateAll();
        }
        // Have to manually build status with room-level lock annotation
        System.out.println("  Status:\n" + kids.getStatus() + " [LOCKED]");
        System.out.println("  Power: " + kids.getTotalPower() + "W");

        System.out.println("\nStep 2 — Unlock and activate:");
        if (0 == roomPin) { roomLocked = false; System.out.println("    >> Unlock SUCCESS"); }
        if (!roomLocked) {
            kids.activateAll();
            roomTimerRunning = true;
        }
        String timerSuffix = roomTimerRunning ? " (auto-off in " + roomTimerSeconds + "s)" : "";
        System.out.println("  Status:\n" + kids.getStatus() + timerSuffix);
        System.out.println("  Power: " + kids.getTotalPower() + "W");

        System.out.println("\nStep 3 — Timer expires (entire room shuts off):");
        if (roomTimerRunning) {
            System.out.println("    >> Timer expired — auto-deactivating.");
            kids.deactivateAll();
            roomTimerRunning = false;
        }
        System.out.println("  Status:\n" + kids.getStatus());
        System.out.println("  Power: " + kids.getTotalPower() + "W");

        System.out.println("\nStep 4 — Add to Home:");
        MessyHome home = new MessyHome("Night Home");
        home.addRoom(kids);
        System.out.println("  Home power: " + home.getTotalPower() + "W");

        // NOTE: prepareForNight as a reusable method is IMPOSSIBLE here.
        // It would need to accept both Light AND Room AND Thermostat...
        // You'd need:
        //
        //   static Object prepareForNight(Object entity) {
        //       if (entity instanceof Light) { ... }
        //       else if (entity instanceof Thermostat) { ... }
        //       else if (entity instanceof MessyRoom) { ... }
        //       // and return what? Object? Cast everywhere?
        //   }
        //
        // This is the point where the design collapses completely.
    }
}
