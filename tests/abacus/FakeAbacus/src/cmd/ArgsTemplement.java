package cmd;
import java.util.*;

public class ArgsTemplement {

    private ArrayList<Option> options = new ArrayList<Option>();

    public ArgsTemplement(String[] args)
    {
        int len = args.length;
        for(int i=0;i<len;i++)
        {
            if(args[i].startsWith("-"))
            {
                String tag = args[i];
                String value = "-";
                if(i+1<len)
                    value = args[i+1];
                if(value.startsWith("-"))
                    options.add(new Option(tag));
                else
                    options.add(new Option(tag, value));
            }
        }
    }

    public boolean specifiedOption(String tag)
    {
        for(Option op : options)
        {
            if(op.optionTag.equals(tag))
                return true;
        }
        return false;
    }

    public String getValue(String tag)
    {
        for(Option op : options)
        {
            if(op.optionTag.equals(tag))
                return op.optionValue;
        }
        return null;
    }
}
