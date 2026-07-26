import cli.Cli;
import cli.CommandHandler;
import io.CsvMenuLoader;
import service.MenuCatalog;
import service.OrderService;
import service.ReceiptService;

/**
 * Main entry point for the FoodFlow application.
 */
public class Main {
    public static void main(String[] args) {
        System.out.println("Starting FoodFlow...\n");

        MenuCatalog catalog = new MenuCatalog();
        OrderService orderService = new OrderService();
        ReceiptService receiptService = new ReceiptService();
        CommandHandler commandHandler = new CommandHandler(catalog, orderService, receiptService);

        if (args.length > 0) {
            System.out.println("Auto-loading menu: " + args[0]);
            commandHandler.handleLoad(args[0]);
        } else {
            try {
                catalog.addAll(new CsvMenuLoader().loadFromFile("data/menu.csv"));
                System.out.println("Loaded default menu from data/menu.csv");
            } catch (Exception e) {
                System.err.println("Could not load default menu: " + e.getMessage());
            }
        }

        Cli cli = new Cli(commandHandler);
        cli.start();
    }
}

