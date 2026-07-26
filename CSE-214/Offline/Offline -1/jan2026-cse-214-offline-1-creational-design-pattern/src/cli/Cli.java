package cli;

import java.util.Scanner;

/**
 * Simple command-line interface.
 */
public class Cli {
    private final CommandHandler commandHandler;
    private final Scanner scanner;
    private boolean running;

    public Cli(CommandHandler commandHandler) {
        this.commandHandler = commandHandler;
        this.scanner = new Scanner(System.in);
    }

    public void start() {
        running = true;
        System.out.println("FoodFlow v0.1");
        System.out.println("Type 'help' for commands.\n");

        while (running) {
            System.out.print("> ");
            String line = scanner.nextLine().trim();
            if (!line.isEmpty()) {
                processCommand(line);
            }
        }
        scanner.close();
    }

    private void processCommand(String line) {
        String[] parts = line.split("\\s+");
        String command = parts[0].toLowerCase();

        try {
            switch (command) {
                case "load":
                    if (parts.length < 2) {
                        System.err.println("Usage: load <menu.csv>");
                    } else {
                        commandHandler.handleLoad(parts[1]);
                    }
                    break;
                case "menu":
                    commandHandler.handleMenu();
                    break;
                case "add":
                    commandHandler.handleAdd(parts);
                    break;
                case "cart":
                    commandHandler.handleCart();
                    break;
                case "clear":
                    commandHandler.handleClear();
                    break;
                case "checkout":
                    commandHandler.handleCheckout(parts);
                    break;
                case "sample":
                    commandHandler.handleSample();
                    break;
                case "receipt":
                    if (parts.length < 2) {
                        System.err.println("Usage: receipt <outpath>");
                    } else {
                        commandHandler.handleReceipt(parts[1]);
                    }
                    break;
                case "help":
                    commandHandler.handleHelp();
                    break;
                case "exit":
                    System.out.println("Bye.");
                    running = false;
                    break;
                default:
                    System.err.println("Unknown command: " + command);
                    break;
            }
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}

