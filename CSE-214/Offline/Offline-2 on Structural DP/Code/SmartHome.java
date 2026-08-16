import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/**
 * SmartHomeDemo.java
 * Contains all the domain models for the Smart Home Automation Hub.
 */

// ============================================================
//  CORE INTERFACE
// ============================================================
interface SmartDevice {
    void activate();
    void deactivate();
    double getPowerUsage();
    String getStatus();
    
    // Crucial for resolving the base type when dealing with heavily decorated devices
    SmartDevice getBaseDevice(); 
}

// ============================================================
//  LEAF DEVICES
// ============================================================
class SmartLight implements SmartDevice {
    private boolean on = false;

    public void activate() { on = true; }
    public void deactivate() { on = false; }
    public double getPowerUsage() { return on ? 10.0 : 0.0; }
    public String getStatus() { return on ? "Light ON" : "Light OFF"; }
    public SmartDevice getBaseDevice() { return this; }
}

class SmartThermostat implements SmartDevice {
    private boolean on = false;

    public void activate() { on = true; }
    public void deactivate() { on = false; }
    public double getPowerUsage() { return on ? 150.0 : 0.0; }
    public String getStatus() { return on ? "Thermostat ON" : "Thermostat OFF"; }
    public SmartDevice getBaseDevice() { return this; }
}

class SmartSpeaker implements SmartDevice {
    private boolean on = false;

    public void activate() { on = true; }
    public void deactivate() { on = false; }
    public double getPowerUsage() { return on ? 5.0 : 0.0; }
    public String getStatus() { return on ? "Speaker ON" : "Speaker OFF"; }
    public SmartDevice getBaseDevice() { return this; }
}

// ============================================================
//  COMPOSITE CLASSES
// ============================================================
class Room implements SmartDevice {
    private String name;
    private List<SmartDevice> devices = new ArrayList<>();

    public Room(String name) {
        this.name = name;
    }

    public void addDevice(SmartDevice device) {
        devices.add(device);
    }

    public List<SmartDevice> getDevices() {
        return devices;
    }

    public void activate() {
        for (SmartDevice device : devices) {
            device.activate();
        }
    }

    public void deactivate() {
        for (SmartDevice device : devices) {
            device.deactivate();
        }
    }

    public double getPowerUsage() {
        double totalPower = 0.0;
        for (SmartDevice device : devices) {
            totalPower += device.getPowerUsage();
        }
        return totalPower;
    }

    public String getStatus() {
        return "Room: " + name;
    }

    public SmartDevice getBaseDevice() { 
        return this; 
    }
}

class Home implements SmartDevice {
    private String name;
    private List<SmartDevice> rooms = new ArrayList<>();

    public Home(String name) {
        this.name = name;
    }

    // Accepts any SmartDevice so that Upgraded/Decorated Rooms can be added
    public void addRoom(SmartDevice room) {
        rooms.add(room);
    }

    public void activate() {
        for (SmartDevice room : rooms) {
            room.activate();
        }
    }

    public void deactivate() {
        for (SmartDevice room : rooms) {
            room.deactivate();
        }
    }

    public double getPowerUsage() {
        double totalPower = 0.0;
        for (SmartDevice room : rooms) {
            totalPower += room.getPowerUsage();
        }
        return totalPower;
    }

    public String getStatus() {
        return "Home: " + name;
    }

    public SmartDevice getBaseDevice() { 
        return this; 
    }
}

// ============================================================
//  DEVICE-LEVEL UPGRADES (DECORATORS)
// ============================================================
class AccessRestricted implements SmartDevice {
    private SmartDevice target;
    private int pin;
    private boolean unlocked = false;

    public AccessRestricted(SmartDevice target, int pin) {
        this.target = target;
        this.pin = pin;
    }

    public void unlock(int enteredPin) {
        if (this.pin == enteredPin) {
            this.unlocked = true;
        }
    }

    public void activate() {
        if (unlocked) {
            target.activate();
        }
    }

    public void deactivate() {
        target.deactivate();
        unlocked = false; // Re-locks upon deactivation
    }

    public double getPowerUsage() {
        return target.getPowerUsage();
    }

    public String getStatus() {
        return target.getStatus() + (unlocked ? "" : " [LOCKED]");
    }

    public SmartDevice getBaseDevice() {
        return target.getBaseDevice();
    }
}

class TimerControlled implements SmartDevice {
    private SmartDevice target;
    private int durationMinutes;
    private boolean timerActive = false;

    public TimerControlled(SmartDevice target, int durationMinutes) {
        this.target = target;
        this.durationMinutes = durationMinutes;
    }

    public void activate() {
        target.activate();
        timerActive = true;
    }

    public void deactivate() {
        target.deactivate();
        timerActive = false;
    }

    public void simulateTimerExpiry() {
        if (timerActive) {
            target.deactivate();
            timerActive = false;
        }
    }

    public double getPowerUsage() {
        return target.getPowerUsage();
    }

    public String getStatus() {
        return target.getStatus() + (timerActive ? " (auto-off active)" : "");
    }

    public SmartDevice getBaseDevice() {
        return target.getBaseDevice();
    }
}

class PowerThrottled implements SmartDevice {
    private SmartDevice target;
    private double maxPower;

    public PowerThrottled(SmartDevice target, double maxPower) {
        this.target = target;
        this.maxPower = maxPower;
    }

    public void activate() { target.activate(); }
    public void deactivate() { target.deactivate(); }

    public double getPowerUsage() {
        return Math.min(target.getPowerUsage(), maxPower);
    }

    public String getStatus() {
        return target.getStatus() + " (throttled)";
    }

    public SmartDevice getBaseDevice() {
        return target.getBaseDevice();
    }
}

// ============================================================
//  ROOM-LEVEL UPGRADES (DECORATORS)
// ============================================================
class EcoMode implements SmartDevice {
    private Room room;
    private double maxPower;

    // Compile-time safety: Forces parameter to be a Room
    public EcoMode(Room room, double maxPower) {
        this.room = room;
        this.maxPower = maxPower;
    }

    public void activate() {
        room.activate(); // Turn everything on first
        
        List<SmartDevice> devices = room.getDevices();
        // Traverse in reverse order (shedding the most recently added devices first)
        for (int i = devices.size() - 1; i >= 0; i--) {
            if (this.getPowerUsage() <= maxPower) {
                break; // Stop shedding once we are under budget
            }
            devices.get(i).deactivate();
        }
    }

    public void deactivate() { room.deactivate(); }

    public double getPowerUsage() {
        return room.getPowerUsage();
    }

    public String getStatus() {
        return room.getStatus() + " [eco-mode]";
    }

    public SmartDevice getBaseDevice() {
        return room.getBaseDevice();
    }
}

class GuestMode implements SmartDevice {
    private Room room;
    private Set<Class<?>> allowedTypes;

    // Compile-time safety: Forces parameter to be a Room
    public GuestMode(Room room, Set<Class<?>> allowedTypes) {
        this.room = room;
        this.allowedTypes = allowedTypes;
    }

    public void activate() {
        for (SmartDevice device : room.getDevices()) {
            // Unpack decorators to find the base identity of the object
            if (allowedTypes.contains(device.getBaseDevice().getClass())) {
                device.activate();
            }
        }
    }

    public void deactivate() { room.deactivate(); }

    public double getPowerUsage() {
        return room.getPowerUsage();
    }

    public String getStatus() {
        return room.getStatus() + " [guest-restricted]";
    }

    public SmartDevice getBaseDevice() {
        return room.getBaseDevice();
    }
}