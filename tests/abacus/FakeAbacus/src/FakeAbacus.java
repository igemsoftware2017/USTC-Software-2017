import java.util.concurrent.TimeUnit;
import cmd.ArgsTemplement;
import java.io.*;

public class FakeAbacus {
    public static void main (String args[]) throws InterruptedException, IOException {
        ArgsTemplement at = new ArgsTemplement(args);

        if (!at.specifiedOption("-in") || !at.specifiedOption("-out")) error();
        String input = at.getValue("-in");
        String output = at.getValue("-out");

        checkFile(input);

        TimeUnit.SECONDS.sleep(1);
        System.out.println("ENERGY");
    }

    public static void error () {
        System.out.println("ERROR");
        System.exit(1);
    }

    public static void checkFile (String name) {
        File f = new File(name);
        System.out.println(name);
        if (!(f.exists() && !f.isDirectory())) error();
    }
}
