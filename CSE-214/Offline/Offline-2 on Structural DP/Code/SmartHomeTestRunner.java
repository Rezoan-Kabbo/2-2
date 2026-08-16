/**
 * SmartHomeTestRunner.java
 *
 * A self-contained test suite for the Smart Home Automation Hub assignment.
 * No JUnit or external libraries needed — just compile and run.
 *
 * Usage:
 *   javac SmartHomeTestRunner.java SmartHomeDemo.java
 *   java SmartHomeTestRunner
 *
 * After every refactor, run this. If anything breaks, you'll know exactly
 * which requirement failed and why.
 */

import java.util.*;

public class SmartHomeTestRunner {

    static int passed = 0;
    static int failed = 0;
    static int totalTests = 0;

    public static void main(String[] args) {

        section("1. LEAF DEVICE BASICS");
        testLightBasics();
        testThermostatBasics();
        testSpeakerBasics();

        section("2. ROOM");
        testRoom();
        testRoomCascadeActivate();
        testRoomCascadeDeactivate();
        testRoomMixedDevices();

        section("3. HOME");
        testHomeAggregation();
        testHomeCascade();

        section("4. Upgrade — ACCESS RESTRICTED");
        testAccessRestrictedBlocksActivation();
        testAccessRestrictedUnlockWrongPin();
        testAccessRestrictedUnlockCorrectPin();
        testAccessRestrictedPowerUnaffected();
        testAccessRestrictedStatusAnnotation();

        section("5. Upgrade — TIMER CONTROLLED");
        testTimerControlledActivation();
        testTimerControlledExpiry();
        testTimerControlledManualDeactivateCancels();
        testTimerControlledStatusAnnotation();

        section("6. Upgrade — POWER THROTTLED");
        testPowerThrottledCaps();
        testPowerThrottledBelowCap();
        testPowerThrottledStatusAnnotation();

        section("7. Multiple Upgrade — DEVICE LEVEL");
        testAccessRestrictedPlusTimerControlled();
        testAccessRestrictedPlusPowerThrottled();
        testTripleStack();

        section("8. UNIFORM INTERFACE");
        testUpdatedDeviceIsSmartDevice();
        testEcoRoomIsSmartDevice();
        testRoomAcceptsUpgradedChildren();

        section("9. ECOMODE FOR ROOM");
        testEcoModeWithinBudget();
        testEcoModeShedsOverBudget();
        testEcoModeShedsInReverseOrder();
        testEcoModePowerReporting();

        section("10. GUESTMODE FOR ROOM");
        testGuestModeAllowedTypes();
        testGuestModeBlocksDisallowed();
        testGuestModePowerOnlyAllowed();
        testGuestModeStatusAnnotation();

        section("11. ORDER SENSITIVITY");
        testThrottledThenEcoVsRawEco();

        section("12. UPGRADED DEVICE ON ROOM");
        testAccessRestrictedOnRoom();
        testTimerControlledOnRoom();
        testPrepareForNightOnRoom();
        testUpgradedRoomAddableToHome();

        section("13. ROOM-LEVEL TYPE SAFETY");
        testEcoModeRejectsLeafAtCompileTime();

        section("14. MIXED SCENARIO");
        testGuestModeWithMixedEnhancements();

        // --------------------------------------------------------
        //  SUMMARY
        // --------------------------------------------------------
        System.out.println("\n" + "=".repeat(55));
        System.out.println("  RESULTS: " + passed + " passed, " + failed + " failed, " + totalTests + " total");
        System.out.println("=".repeat(55));

        if (failed == 0) {
            System.out.println("  ALL TESTS PASSED");
        } else {
            System.out.println("  SOME TESTS FAILED — review output above");
        }

        System.exit(failed > 0 ? 1 : 0);
    }

    // ============================================================
    //  1. LEAF DEVICE BASICS
    // ============================================================

    static void testLightBasics() {
        SmartLight l = new SmartLight();
        assertEquals("Light off initially", 0.0, l.getPowerUsage());
        l.activate();
        assertEquals("Light on power", 10.0, l.getPowerUsage());
        assertContains("Light on status", l.getStatus(), "ON");
        l.deactivate();
        assertEquals("Light off power", 0.0, l.getPowerUsage());
    }

    static void testThermostatBasics() {
        SmartThermostat t = new SmartThermostat();
        assertEquals("Thermostat off initially", 0.0, t.getPowerUsage());
        t.activate();
        assertEquals("Thermostat on power", 150.0, t.getPowerUsage());
        t.deactivate();
        assertEquals("Thermostat off power", 0.0, t.getPowerUsage());
    }

    static void testSpeakerBasics() {
        SmartSpeaker s = new SmartSpeaker();
        assertEquals("Speaker off initially", 0.0, s.getPowerUsage());
        s.activate();
        assertEquals("Speaker on power", 5.0, s.getPowerUsage());
        s.deactivate();
        assertEquals("Speaker off power", 0.0, s.getPowerUsage());
    }

    // ============================================================
    //  2. ROOM
    // ============================================================

    static void testRoom() {
        Room r = new Room("Test");
        r.addDevice(new SmartLight());
        r.addDevice(new SmartThermostat());
        assertEquals("Room inactive power", 0.0, r.getPowerUsage());
    }

    static void testRoomCascadeActivate() {
        Room r = new Room("Test");
        r.addDevice(new SmartLight());
        r.addDevice(new SmartThermostat());
        r.activate();
        assertEquals("Room active power", 160.0, r.getPowerUsage());
    }

    static void testRoomCascadeDeactivate() {
        Room r = new Room("Test");
        SmartLight l = new SmartLight();
        l.activate();
        r.addDevice(l);
        r.deactivate();
        assertEquals("Room deactivated power", 0.0, r.getPowerUsage());
    }

    static void testRoomMixedDevices() {
        Room r = new Room("Test");
        r.addDevice(new SmartLight());      // 10W
        r.addDevice(new SmartLight());      // 10W
        r.addDevice(new SmartSpeaker());    // 5W
        r.activate();
        assertEquals("Room 2 lights + speaker", 25.0, r.getPowerUsage());
    }

    // ============================================================
    //  3. HOME
    // ============================================================

    static void testHomeAggregation() {
        Room r1 = new Room("R1");
        r1.addDevice(new SmartLight());

        Room r2 = new Room("R2");
        r2.addDevice(new SmartThermostat());

        Home h = new Home("H");
        h.addRoom(r1);
        h.addRoom(r2);
        h.activate();
        assertEquals("Home total power", 160.0, h.getPowerUsage());
    }

    static void testHomeCascade() {
        Room r1 = new Room("R1");
        r1.addDevice(new SmartLight());
        r1.addDevice(new SmartSpeaker());

        Home h = new Home("H");
        h.addRoom(r1);
        h.activate();
        assertEquals("Home activated", 15.0, h.getPowerUsage());
        h.deactivate();
        assertEquals("Home deactivated", 0.0, h.getPowerUsage());
    }

    // ============================================================
    //  4. ACCESS RESTRICTION TEST
    // ============================================================

    static void testAccessRestrictedBlocksActivation() {
        AccessRestricted ar = new AccessRestricted(new SmartLight(), 1234);
        ar.activate();
        assertEquals("Locked light stays off", 0.0, ar.getPowerUsage());
    }

    static void testAccessRestrictedUnlockWrongPin() {
        AccessRestricted ar = new AccessRestricted(new SmartLight(), 1234);
        ar.unlock(0000);
        ar.activate();
        assertEquals("Wrong PIN still locked", 0.0, ar.getPowerUsage());
    }

    static void testAccessRestrictedUnlockCorrectPin() {
        AccessRestricted ar = new AccessRestricted(new SmartLight(), 1234);
        ar.unlock(1234);
        ar.activate();
        assertEquals("Correct PIN unlocks", 10.0, ar.getPowerUsage());
    }

    static void testAccessRestrictedPowerUnaffected() {
        SmartLight l = new SmartLight();
        l.activate();   // turn on BEFORE locking
        AccessRestricted ar = new AccessRestricted(l, 1234);
        // Locked but already running — power should still report
        assertEquals("Locked but running device reports power", 10.0, ar.getPowerUsage());
    }

    static void testAccessRestrictedStatusAnnotation() {
        AccessRestricted ar = new AccessRestricted(new SmartLight(), 1234);
        assertContains("Locked status annotation", ar.getStatus(), "LOCKED");
        ar.unlock(1234);
        assertNotContains("Unlocked no annotation", ar.getStatus(), "LOCKED");
    }

    // ============================================================
    //  5. TIMER CONTROL
    // ============================================================

    static void testTimerControlledActivation() {
        TimerControlled tc = new TimerControlled(new SmartLight(), 60);
        tc.activate();
        assertEquals("Timer device active", 10.0, tc.getPowerUsage());
    }

    static void testTimerControlledExpiry() {
        TimerControlled tc = new TimerControlled(new SmartLight(), 60);
        tc.activate();
        tc.simulateTimerExpiry();
        assertEquals("Timer expired, device off", 0.0, tc.getPowerUsage());
    }

    static void testTimerControlledManualDeactivateCancels() {
        TimerControlled tc = new TimerControlled(new SmartLight(), 60);
        tc.activate();
        tc.deactivate();
        // After manual deactivate, simulateTimerExpiry should do nothing
        tc.simulateTimerExpiry();
        assertEquals("Manual deactivate cancels timer", 0.0, tc.getPowerUsage());
    }

    static void testTimerControlledStatusAnnotation() {
        TimerControlled tc = new TimerControlled(new SmartLight(), 60);
        tc.activate();
        assertContains("Timer status annotation", tc.getStatus(), "auto-off");
        tc.deactivate();
        assertNotContains("No timer annotation when off", tc.getStatus(), "auto-off");
    }

    // ============================================================
    //  6. POWER THROTTLE
    // ============================================================

    static void testPowerThrottledCaps() {
        PowerThrottled pt = new PowerThrottled(new SmartThermostat(), 80);
        pt.activate();
        assertEquals("Throttled 150W to 80W", 80.0, pt.getPowerUsage());
    }

    static void testPowerThrottledBelowCap() {
        PowerThrottled pt = new PowerThrottled(new SmartLight(), 50);
        pt.activate();
        assertEquals("10W under 50W cap unchanged", 10.0, pt.getPowerUsage());
    }

    static void testPowerThrottledStatusAnnotation() {
        PowerThrottled pt = new PowerThrottled(new SmartThermostat(), 80);
        pt.activate();
        assertContains("Throttled status annotation", pt.getStatus(), "throttled");
    }

    // ============================================================
    //  7. Multiple Upgrade
    // ============================================================

    static void testAccessRestrictedPlusTimerControlled() {
        AccessRestricted ar = new AccessRestricted(new SmartLight(), 1234);
        TimerControlled tc = new TimerControlled(ar, 60);

        // Locked: activate should fail
        tc.activate();
        assertEquals("Locked + timed: light stays off", 0.0, tc.getPowerUsage());

        // Unlock and activate
        ar.unlock(1234);
        tc.activate();
        assertEquals("Unlocked + timed: light on", 10.0, tc.getPowerUsage());

        // Timer expires
        tc.simulateTimerExpiry();
        assertEquals("Timer expired: light off", 0.0, tc.getPowerUsage());
    }

    static void testAccessRestrictedPlusPowerThrottled() {
        AccessRestricted ar = new AccessRestricted(new SmartThermostat(), 5555);
        PowerThrottled pt = new PowerThrottled(ar, 80);
        ar.unlock(5555);
        pt.activate();
        assertEquals("Unlocked + throttled", 80.0, pt.getPowerUsage());
    }

    static void testTripleStack() {
        AccessRestricted ar = new AccessRestricted(new SmartThermostat(), 1111);
        PowerThrottled pt = new PowerThrottled(ar, 80);
        TimerControlled tc = new TimerControlled(pt, 120);

        // All locked
        tc.activate();
        assertEquals("Triple stack locked", 0.0, tc.getPowerUsage());

        // Unlock, activate, verify throttle
        ar.unlock(1111);
        tc.activate();
        assertEquals("Triple stack unlocked + throttled", 80.0, tc.getPowerUsage());
        assertContains("Triple stack timer annotation", tc.getStatus(), "auto-off");

        // Timer expires
        tc.simulateTimerExpiry();
        assertEquals("Triple stack timer expired", 0.0, tc.getPowerUsage());
    }

    // ============================================================
    //  8. UNIFORM INTERFACE
    // ============================================================

    static void testUpdatedDeviceIsSmartDevice() {
        SmartDevice d = new AccessRestricted(new SmartLight(), 1234);
        assertNotNull("Upgraded device is SmartDevice", d);
        // Should compile and work — if this method runs, the type check passed
        assertTrue("Upgraded device has status", d.getStatus() != null);
    }

    static void testEcoRoomIsSmartDevice() {
        Room r = new Room("Test");
        r.addDevice(new SmartLight());
        SmartDevice d = new EcoMode(r, 100);
        assertNotNull("Eco room is SmartDevice", d);
        assertTrue("Eco room has status", d.getStatus() != null);
    }

    static void testRoomAcceptsUpgradedChildren() {
        Room r = new Room("Test");
        r.addDevice(new SmartLight());                                 // plain
        r.addDevice(new AccessRestricted(new SmartThermostat(), 1234));  // upgraded
        r.addDevice(new PowerThrottled(new SmartLight(), 5));            // upgraded
        r.activate();
        // Only plain light and throttled light should be on (thermostat is locked)
        // plain light = 10W, throttled light = 5W, locked thermostat = 0W
        assertEquals("Room with mixed children", 15.0, r.getPowerUsage());
    }

    // ============================================================
    //  9. ECOMODE — ROOM LEVEL
    // ============================================================

    static void testEcoModeWithinBudget() {
        Room r = new Room("Test");
        r.addDevice(new SmartLight());   // 10W
        r.addDevice(new SmartLight());   // 10W
        SmartDevice eco = new EcoMode(r, 100);
        eco.activate();
        assertEquals("EcoMode within budget", 20.0, eco.getPowerUsage());
    }

    static void testEcoModeShedsOverBudget() {
        Room r = new Room("Test");
        r.addDevice(new SmartLight());       // 10W
        r.addDevice(new SmartThermostat());  // 150W
        SmartDevice eco = new EcoMode(r, 100);
        eco.activate();
        // Thermostat (last added) should be shed: 10W remains
        assertTrue("EcoMode sheds to fit budget", eco.getPowerUsage() <= 100);
    }

    static void testEcoModeShedsInReverseOrder() {
        Room r = new Room("Test");
        SmartLight l1 = new SmartLight();
        SmartLight l2 = new SmartLight();
        SmartThermostat t = new SmartThermostat();
        r.addDevice(l1);   // 10W  — index 0, added first
        r.addDevice(l2);   // 10W  — index 1
        r.addDevice(t);    // 150W — index 2, added last → shed first
        SmartDevice eco = new EcoMode(r, 100);
        eco.activate();
        // Thermostat (last) should be shed first, lights remain
        assertEquals("First light stays on", 10.0, l1.getPowerUsage());
        assertEquals("Second light stays on", 10.0, l2.getPowerUsage());
        assertEquals("Thermostat shed", 0.0, t.getPowerUsage());
    }

    static void testEcoModePowerReporting() {
        Room r = new Room("Test");
        r.addDevice(new SmartLight());       // 10W
        r.addDevice(new SmartLight());       // 10W
        r.addDevice(new SmartThermostat());  // 150W
        SmartDevice eco = new EcoMode(r, 100);
        eco.activate();
        // After shedding, power should not exceed budget
        assertTrue("EcoMode power <= budget", eco.getPowerUsage() <= 100);
    }

    // ============================================================
    //  10. GUESTMODE — ROOM LEVEL
    // ============================================================

    static void testGuestModeAllowedTypes() {
        Room r = new Room("Test");
        SmartLight l = new SmartLight();
        SmartSpeaker s = new SmartSpeaker();
        r.addDevice(l);
        r.addDevice(s);

        Set<Class<?>> allowed = new HashSet<>(Arrays.asList(SmartLight.class, SmartSpeaker.class));
        SmartDevice gm = new GuestMode(r, allowed);
        gm.activate();
        assertEquals("Light allowed", 10.0, l.getPowerUsage());
        assertEquals("Speaker allowed", 5.0, s.getPowerUsage());
    }

    static void testGuestModeBlocksDisallowed() {
        Room r = new Room("Test");
        SmartThermostat t = new SmartThermostat();
        SmartLight l = new SmartLight();
        r.addDevice(t);
        r.addDevice(l);

        Set<Class<?>> allowed = new HashSet<>(Arrays.asList(SmartLight.class));
        SmartDevice gm = new GuestMode(r, allowed);
        gm.activate();
        assertEquals("Thermostat blocked by guest mode", 0.0, t.getPowerUsage());
        assertEquals("Light allowed through guest mode", 10.0, l.getPowerUsage());
    }

    static void testGuestModePowerOnlyAllowed() {
        Room r = new Room("Test");
        r.addDevice(new SmartLight());       // 10W — allowed
        r.addDevice(new SmartThermostat());  // 150W — blocked
        r.addDevice(new SmartSpeaker());     // 5W — allowed

        Set<Class<?>> allowed = new HashSet<>(Arrays.asList(SmartLight.class, SmartSpeaker.class));
        SmartDevice gm = new GuestMode(r, allowed);
        gm.activate();
        assertEquals("Guest power = allowed only", 15.0, gm.getPowerUsage());
    }

    static void testGuestModeStatusAnnotation() {
        Room r = new Room("Test");
        r.addDevice(new SmartThermostat());

        Set<Class<?>> allowed = new HashSet<>(Arrays.asList(SmartLight.class));
        SmartDevice gm = new GuestMode(r, allowed);
        assertContains("Guest restricted annotation", gm.getStatus(), "guest-restricted");
    }

    // ============================================================
    //  11. ORDER SENSITIVITY
    // ============================================================

    static void testThrottledThenEcoVsRawEco() {
        // Setup 1: Throttle to 80W first, then EcoMode 100W
        Room r1 = new Room("S1");
        r1.addDevice(new SmartLight());                                // 10W
        r1.addDevice(new SmartLight());                                // 10W
        r1.addDevice(new PowerThrottled(new SmartThermostat(), 80));   // 80W
        SmartDevice eco1 = new EcoMode(r1, 100);
        eco1.activate();
        double power1 = eco1.getPowerUsage();

        // Setup 2: Raw thermostat, EcoMode 100W
        Room r2 = new Room("S2");
        r2.addDevice(new SmartLight());       // 10W
        r2.addDevice(new SmartLight());       // 10W
        r2.addDevice(new SmartThermostat());  // 150W
        SmartDevice eco2 = new EcoMode(r2, 100);
        eco2.activate();
        double power2 = eco2.getPowerUsage();

        assertTrue("Order produces different results (p1=" + power1 + " vs p2=" + power2 + ")",
                   power1 != power2);

        // Setup 1 should keep all devices (10+10+80=100), setup 2 sheds thermostat (10+10=20)
        assertTrue("Throttled version keeps more devices", power1 > power2);
    }

    // ============================================================
    //  12. UPGRADED DEVICE ON ROOM
    // ============================================================

    static void testAccessRestrictedOnRoom() {
        Room r = new Room("Test");
        r.addDevice(new SmartLight());
        r.addDevice(new SmartSpeaker());
        AccessRestricted ar = new AccessRestricted(r, 0);

        ar.activate();
        assertEquals("Locked room: nothing activates", 0.0, ar.getPowerUsage());

        ar.unlock(0);
        ar.activate();
        assertEquals("Unlocked room: all activate", 15.0, ar.getPowerUsage());
    }

    static void testTimerControlledOnRoom() {
        Room r = new Room("Test");
        r.addDevice(new SmartLight());
        r.addDevice(new SmartThermostat());
        TimerControlled tc = new TimerControlled(r, 3600);

        tc.activate();
        assertEquals("Timed room active", 160.0, tc.getPowerUsage());

        tc.simulateTimerExpiry();
        assertEquals("Timed room expired", 0.0, tc.getPowerUsage());
    }

    static void testPrepareForNightOnRoom() {
        Room r = new Room("Kids");
        r.addDevice(new SmartLight());
        r.addDevice(new SmartSpeaker());
        r.addDevice(new SmartThermostat());

        SmartDevice night = prepareForNight(r);

        // Should be locked
        night.activate();
        assertEquals("Night room locked", 0.0, night.getPowerUsage());
    }

    static void testUpgradedRoomAddableToHome() {
        Room r = new Room("Test");
        r.addDevice(new SmartLight());
        SmartDevice upgraded = new TimerControlled(new AccessRestricted(r, 0), 3600);

        Home h = new Home("H");
        h.addRoom(upgraded);
        // Should compile and work — upgraded room is a SmartDevice
        assertTrue("Upgraded room in home", h.getStatus() != null);
        assertEquals("Home with locked room", 0.0, h.getPowerUsage());
    }

    // ============================================================
    //  13. ROOM-LEVEL TYPE SAFETY
    // ============================================================

    static void testEcoModeRejectsLeafAtCompileTime() {
        // This test documents the compile-time constraint.
        // If your EcoMode constructor accepts Room (not SmartDevice),
        // then the following line should NOT compile:
        //
        //     new EcoMode(new SmartLight(), 100);  // SHOULD NOT COMPILE
        //
        // We can't test a compile error at runtime, so this test just
        // verifies that EcoMode works correctly with a Room.
        Room r = new Room("Test");
        r.addDevice(new SmartLight());
        SmartDevice eco = new EcoMode(r, 100);
        eco.activate();
        assertTrue("EcoMode accepts Room", eco.getPowerUsage() <= 100);
    }

    // ============================================================
    //  14. MIXED SCENARIO
    // ============================================================

    static void testGuestModeWithMixedEnhancements() {
        Room r = new Room("Guest");
        SmartSpeaker speaker = new SmartSpeaker();
        SmartThermostat thermo = new SmartThermostat();
        SmartLight light = new SmartLight();

        r.addDevice(speaker);
        r.addDevice(new AccessRestricted(thermo, 9999));  // locked
        r.addDevice(new TimerControlled(light, 120));      // timed

        Set<Class<?>> allowed = new HashSet<>(Arrays.asList(SmartLight.class, SmartSpeaker.class));
        SmartDevice gm = new GuestMode(r, allowed);
        gm.activate();

        assertEquals("Speaker activated", 5.0, speaker.getPowerUsage());
        assertEquals("Thermostat blocked", 0.0, thermo.getPowerUsage());
        assertEquals("Light activated", 10.0, light.getPowerUsage());
        assertEquals("Guest power total", 15.0, gm.getPowerUsage());
        assertContains("Guest restricted annotation", gm.getStatus(), "guest-restricted");
    }

    // ============================================================
    //  HELPER 
    // ============================================================

    static SmartDevice prepareForNight(SmartDevice entity) {
        return new TimerControlled(new AccessRestricted(entity, 0), 3600);
    }

    // ============================================================
    //  ASSERTION UTILITIES
    // ============================================================

    static void assertEquals(String testName, double expected, double actual) {
        totalTests++;
        if (Math.abs(expected - actual) < 0.001) {
            passed++;
            System.out.println("  PASS  " + testName);
        } else {
            failed++;
            System.out.println("  FAIL  " + testName + "  (expected " + expected + ", got " + actual + ")");
        }
    }

    static void assertTrue(String testName, boolean condition) {
        totalTests++;
        if (condition) {
            passed++;
            System.out.println("  PASS  " + testName);
        } else {
            failed++;
            System.out.println("  FAIL  " + testName);
        }
    }

    static void assertNotNull(String testName, Object obj) {
        assertTrue(testName, obj != null);
    }

    static void assertContains(String testName, String haystack, String needle) {
        totalTests++;
        if (haystack != null && haystack.toLowerCase().contains(needle.toLowerCase())) {
            passed++;
            System.out.println("  PASS  " + testName);
        } else {
            failed++;
            System.out.println("  FAIL  " + testName + "  ('" + needle + "' not found in '" + haystack + "')");
        }
    }

    static void assertNotContains(String testName, String haystack, String needle) {
        totalTests++;
        if (haystack == null || !haystack.toLowerCase().contains(needle.toLowerCase())) {
            passed++;
            System.out.println("  PASS  " + testName);
        } else {
            failed++;
            System.out.println("  FAIL  " + testName + "  ('" + needle + "' unexpectedly found in '" + haystack + "')");
        }
    }

    static void section(String title) {
        System.out.println("\n--- " + title + " ---");
    }
}
